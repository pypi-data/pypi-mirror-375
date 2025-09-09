from celery_tasks import run_test
import time

# Define test configurations
TEST_CONFIGS = {
    "test_case_1": {"param1": 10, "param2": "valueA"},
    "test_case_2": {"param1": 20, "param2": "valueB"},
    "test_case_3": {"param1": 30, "param2": "valueC"},
}

if __name__ == "__main__":
    jobs = []
    
    for config, params in TEST_CONFIGS.items():
        job = run_test.apply_async(args=[config, params])
        jobs.append(job)
    
    # Wait for results
    for job in jobs:
        result = job.get(timeout=300)  # Wait for up to 5 minutes per job
        print(f"Completed: {result}")

