from task.JobCore import JobCore


# joblist = [175,176,177,178,179]
joblist = [177,178,179]
job_core = JobCore()
for jobid in joblist:
    print(f"开始运行作业：{jobid}-----------------------------------")
    res = job_core.run_job(jobid=jobid)
    print(f"{jobid} - {res}")
    if res.is_fail():
        exit(1)




