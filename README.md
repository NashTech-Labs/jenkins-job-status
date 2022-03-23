# jenkins-job-status

A SIMPLE PYTHONIC SCRIPT THAT WILL SCRAP DATA FROM JENKINS BY GIVEN JOB URL. 

## Usage

````
./scrape_jenkins_job.py --help                                                                                                                                                          ─╯
usage: scrape_jenkins_job.py [-h] --job JOB --filename FILENAME [--step]

Scrap Jenkins Job Metrics from API endpoints

optional arguments:
  -h, --help            show this help message and exit
  --job JOB, -j JOB     Please enter jenkins Job URL Example: http://localhost:8080/job/portal/job/publish/job/master/ Note: forward slash in the end is needed
  --filename FILENAME, -f FILENAME
                        File name is used for creating CSV files in the current folder script running Example: portal_cube0branhch
  --step, -s            This is used for pipeline step duration calucation, add -s if you want to calculate timestamp for each pipeline steps Note: Your jenkins should be pipeline job
````


## Output 

- If -s flag not specified then the output is in csv file. 
- If -s flag specified then the output is in xlsx file.

