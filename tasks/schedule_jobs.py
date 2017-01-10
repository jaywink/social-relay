import schedule
import time


if __name__ == '__main__':
    print("Scheduling all jobs")
    from tasks.fetch_pod_list import schedule_job
    schedule_job()
    from tasks.poll_pods import schedule_job
    schedule_job()

    while True:
        schedule.run_pending()
        time.sleep(1)
