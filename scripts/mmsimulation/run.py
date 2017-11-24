#!/usr/bin/env python3
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import event
from sqlalchemy import create_engine
import os.path
from shutil import rmtree
import glob
import re
from subprocess import call, check_output, CalledProcessError, STDOUT, DEVNULL
import argparse


Base = declarative_base()


class CompilationError(Exception):
   def __init__(self, message, logfile_path):
      self.message = message
      self.logfile_path = logfile_path


def run_list(s, session=None):
   """ Parse the input string for job numbers.

   The parsing supports the following syntaxes:
      - a single integer (e.g. '1')
      - a range (e.g. '1-4')
      - a list (e.g. '[1-3, 6, 11]')
   """
   # Just an integer
   if re.match('^[0-9]*$', s):
      return [ int(s) ]

   # Range of runs
   if re.match('^[0-9]*\-[0-9]*$', s):
      run_low, run_high = map(int, s.split('-'))
      if run_low > run_high:
         raise argparse.ArgumentTypeError('List range of jobs in ascending order. (e.g. 1-8 not 8-1)')
      return list(range(run_low, run_high + 1))

   # List of runs
   if s.startswith('[') and s.endswith(']'):
      jobs = []
      s = s[1:-1].replace(' ', '')
      for item in s.split(','):
         if re.match('^[0-9]*\-[0-9]*', item):
            run_low, run_high = map(int, item.split('-'))
            if run_low > run_high:
               raise argparse.ArgumentTypeError('List range of jobs in ascending order. (e.g. 1-8 not 8-1)')
            jobs += list(range(run_low, run_high + 1))
         else:
            jobs.append(int(item))
      return jobs

   # Check if its a group name
   if session:
      group_query = session.query(RunGroup).filter(RunGroup.name == s)
      if group_query.count() == 1:
         group = group_query.one()
         runs_query = session.query(Run).filter(Run.group_id == group.id)
         result = []
         for run in runs_query.all():
            result.append(run.id)
         return result

   raise argparse.ArgumentTypeError


class RunGroup(Base):
   __tablename__ = 'rungroup'
   id = Column(Integer, primary_key=True)
   name = Column(String(250), nullable=False)
   description = Column(String(1000))


class Run(Base):
   __tablename__ = 'run'

   id = Column(Integer, primary_key=True)
   name = Column(String(250))
   group_id = Column(Integer, ForeignKey('rungroup.id'))
   group = relationship(RunGroup)
   message = Column(String(1000))
   run_path = Column(String(300))
   output_path = Column(String(300))
   abs_run_path = Column(String(300))
   abs_output_path = Column(String(300))
   created_at = Column(DateTime)
   last_run_particleconversion = Column(DateTime)
   last_run_drift = Column(DateTime)
   last_run_avalanche = Column(DateTime)

   def get_id(self):
      return '{:0>4}'.format(self.id) if self.id else None

   def get_run_path(self):
      if self.abs_run_path:
         return self.abs_run_path
      path = os.path.expandvars(self.run_path)
      if self.group:
         path = path.replace('$GROUPNAME', self.group.name)
      return path

   def get_output_path(self):
      if self.abs_output_path:
         return self.abs_output_path
      path = os.path.expandvars(self.output_path)
      if self.group:
         path = path.replace('$GROUPNAME', self.group.name)
      return path   

   def create_folders(self):
      # Create necessary folders
      if not os.path.exists(self.get_run_path()):
         os.makedirs(self.get_run_path())
      if not os.path.exists(self.get_output_path()):
         os.makedirs(self.get_output_path())

   def delete_folders(self):
      if os.path.exists(self.get_run_path()):
         rmtree(self.get_run_path())
      if os.path.exists(self.get_output_path()):
         rmtree(self.get_output_path())

   def compile(self, recompile=False):
      """ Call the compile script. """
      logfile_path = os.path.join(self.get_run_path(), 'make.log')
      try:
         build_result = check_output(os.path.expandvars(
            f'{os.path.abspath(os.path.dirname(__file__))}/compile_run.sh {self.get_run_path()}'),
               shell=True, stderr=STDOUT)
      except CalledProcessError as e:
         if not recompile:
            self.delete_folders()
         raise CompilationError(build_result, logfile_path)

   def join(self, force=False):
      """ Join the output file. """
      # Try to join drift
      if (glob.glob(os.path.join(self.get_output_path(), '*_drift.root'))
            and (not os.path.exists(os.path.join(self.get_output_path(), 'drift.root'))
               or force)):
         print('Joining drift for job {:0>4}'.format(self.id))
         check_output(os.path.expandvars(
            ('$MICROMEGAS_SCRIPTS_PATH/job_join'
             ' {output_path}/drift.root {output_path}/*_drift.root').format(
                output_path=self.get_output_path())), shell=True)

      # Try to join avalanche
      if (glob.glob(os.path.join(self.get_output_path(), '*_avalanche.root'))
            and (not os.path.exists(os.path.join(self.get_output_path(), 'avalanche.root'))
               or force)):
         print('Joining avalanche for job {:0>4}'.format(self.id))
         check_output(os.path.expandvars(
            ('$MICROMEGAS_SCRIPTS_PATH/job_join {output_path}/avalanche.root'
             ' {output_path}/*_avalanche.root').format(
                output_path=self.get_output_path())), shell=True)


@event.listens_for(Run, 'before_delete')
def __run_delete(mapper, connection, target):
   rmtree(target.get_output_path())
   rmtree(target.get_run_path())
