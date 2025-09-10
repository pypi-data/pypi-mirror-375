from nodejobs.processes import Processes
from nodejobs.jobdb import JobDB, JobFilter, JobRecord, JobRecordDict
from pathlib import Path
import os
import time
from psutil import Process
from typing import Tuple, Union, List
import subprocess


class Jobs:
    def __init__(self, db_path=None, verbose=False):
        self.verbose = verbose
        try:
            # print(f"a. DB jobs working in {db_path }")
            self.db_path = db_path
            os.makedirs(self.db_path, exist_ok=True)
        except Exception as e:

            home = Path.home()
            default_dir = os.path.join(home, "tmp_decelium_job_database")
            os.makedirs(default_dir, exist_ok=True)
            self.db_path = default_dir
            print(f"Jobs.__init__ ({e}). DB jobs working in {self.db_path}")
        self.jobdb = JobDB(self.db_path)
        self.processes = Processes(self.jobdb, verbose)

    def __find(self, job_id: str):
        assert job_id is not None, "can only select by job_id"
        job = None
        jobs = {}
        if job_id is not None:
            jobs = self.jobdb.list_status({"self_id": job_id})
        if len(jobs) > 0:
            job = list(jobs.values())[0]
        return job

    def run(self, command: Union[str, List[str]], job_id: str, cwd: str = None):

        assert len(job_id) > 0, " Job name too short"
        if cwd is None:
            cwd = os.getcwd()
        logdir = f"{self.db_path}/job_logs/"
        os.makedirs(logdir, exist_ok=True)

        logfile = job_id
        self.jobdb.update_status(
            JobRecord(
                {
                    JobRecord.self_id: job_id,
                    JobRecord.last_pid: -1,
                    JobRecord.dirname: job_id,
                    JobRecord.cwd: cwd,
                    JobRecord.logdir: logdir,
                    JobRecord.logfile: logfile,
                    JobRecord.status: JobRecord.Status.c_starting,
                }
            )
        )
        if command is str:
            command = command.strip()
            command = command.split(' ')
        start_proc: subprocess.Popen = self.processes.run(
            command=command,
            job_id=job_id,
            cwd=cwd,
            logdir=logdir,
            logfile=logfile
        )
        cond = isinstance(start_proc, subprocess.Popen)
        assert cond, "Invalid process detected"
        time.sleep(0.5)
        ret = start_proc.poll()
        # print(f"looking at pid {start_proc.pid}")
        if ret is None:
            result = JobRecord(
                {
                    JobRecord.self_id: job_id,
                    JobRecord.status: JobRecord.Status.c_running,
                    JobRecord.last_pid: start_proc.pid,
                }
            )
        elif ret == 0:
            result = JobRecord(
                {
                    JobRecord.self_id: job_id,
                    JobRecord.status: JobRecord.Status.c_finished,
                    JobRecord.last_pid: start_proc.pid,
                }
            )
        else:
            result = JobRecord(
                {
                    JobRecord.self_id: job_id,
                    JobRecord.status: JobRecord.Status.c_failed_start,
                    JobRecord.last_pid: start_proc.pid,
                }
            )

        self.jobdb.update_status(result)
        return result

    def stop(self, job_id: str, wait_time: int = 1) -> JobRecord:

        assert job_id is not None, "can only select by  job_id"
        job: JobRecord = self.__find(job_id)
        if job is None:
            return None
        job = JobRecord(job)
        job_id = job.self_id
        self.jobdb.update_status(
            JobRecord(
                {JobRecord.self_id: job_id,
                 JobRecord.status: job.Status.c_stopping}
            )
        )
        success = self.processes.stop(job_id=job_id)
        time.sleep(wait_time)
        found_job = self.list_status(
            JobFilter(
                {
                    JobFilter.self_id: job_id,
                }
            )
        )
        assert (
            job_id in found_job
        ), "Could not find a job that was just present. \
            Should be impossible. Race condition?"
        job = found_job[job_id]
        if JobRecord(found_job[job_id]).status == JobRecord.Status.c_running:
            if self.verbose is True:
                print(f"inspecting job (A): {job} -- {job_id}")
            result = JobRecord(
                {
                    JobRecord.last_pid: job.last_pid,
                    JobRecord.self_id: job_id,
                    JobRecord.status: job.Status.c_failed_stop,
                }
            )

        if success:
            if self.verbose is True:
                print(f"inspecting job (B): {job}")
            result = JobRecord(
                {
                    JobRecord.last_pid: job.last_pid,
                    JobRecord.self_id: job.self_id,
                    JobRecord.status: job.status,
                }
            )
        else:
            if self.verbose is True:
                print(f"inspecting job (C): {job}")
            result = JobRecord(
                {
                    job.last_pid: job.last_pid,
                    job.self_id: job.self_id,
                    job.status: job.status,
                }
            )
        db_res = self.jobdb.update_status(result)
        if self.verbose is True:
            print(f"inspecting job (D): {db_res}")
        return result

    def job_logs(self, job_id: str) -> Tuple[str, str]:

        job = self.__find(job_id)
        if job is None:
            return (
                f"error: could not find job_id for {job_id}",
                f"error: could not find job_id for {job_id}",
            )
        job = JobRecord(job)
        job_id = job.self_id
        stdlog, errlog = self.jobdb.job_logs(self_id=job_id)
        return stdlog, errlog

    def _update_status(self):
        running_jobs = {}
        if self.verbose is True:
            print("...updating ...")

        for proc in self.processes.list():
            proc: Process = proc
            if self.verbose is True:
                print(f"...updating proc ... {proc}, as {proc.job_id} ")
            try:
                os.waitpid(proc.pid, os.WNOHANG)
            except Exception as e:
                e
                pass
            running_jobs[proc.job_id] = (
                proc
            )
        running_ids = list(running_jobs.keys())
        if self.verbose is True:
            print(f"...updating ... running_ids {running_ids}")

        for actually_running_id in running_ids:
            self.jobdb.update_status(
                JobRecord(
                    {
                        JobRecord.self_id: actually_running_id,
                        JobRecord.status: JobRecord.Status.c_running,
                    }
                )
            )

        db_runningdict = self.jobdb.list_status(
            JobFilter({JobRecord.status: JobRecord.Status.c_running})
        )
        db_stopping_dict = self.jobdb.list_status(
            JobFilter({JobRecord.status: JobRecord.Status.c_stopping})
        )
        db_review_dict = {**db_runningdict, **db_stopping_dict}
        if self.verbose is True:
            print(f"...updating ... db_running_list {running_ids}")

        for job_id in db_review_dict.keys():
            if self.verbose is True:
                print(f"...reviewing {job_id}")
            if job_id not in running_ids:
                # TODO - Review reason for stop to assign correct final status
                # print(f"RETIRING {job_id}")
                stdlog, errlog = self.jobdb.job_logs(self_id=job_id)
                if len(errlog.strip()) > 0:
                    if self.verbose is True:
                        print(f"...recording failed: \nstdlog{stdlog}:\n\nerrlog{errlog}")
                    if job_id in db_stopping_dict:
                        self.jobdb.update_status(
                            JobRecord(
                                {
                                    JobRecord.self_id: job_id,
                                    JobRecord.status: JobRecord.Status.c_stopped,
                                }
                            )
                        )
                else:
                    self.jobdb.update_status(
                        JobRecord(
                            {
                                JobRecord.self_id: job_id,
                                JobRecord.status: JobRecord.Status.c_finished_2,
                            }
                        )
                    )

    def list_status(self, filter=None) -> JobRecordDict:
        # print(f"------------------- A {filter}")
        if filter is None:
            filter = {}
        filter = JobFilter(filter)
        # print(f"------------------- B {filter}")
        self._update_status()
        # print(f"------------------- C {filter}")
        return JobRecordDict(self.jobdb.list_status(filter))

    def get_status(self, job_id: str) -> JobRecord:

        assert job_id, "can only select by job_id"

        # Build a filter for list_status
        filt = {JobFilter.self_id: job_id}

        # list_status returns a JobRecordDict (mapping IDs to JobRecord)
        recs = self.list_status(filt)
        if not recs:
            return None

        # Return the first JobRecord in that dict
        return next(iter(recs.values()))
