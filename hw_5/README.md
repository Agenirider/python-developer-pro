#Architecture

Threads

#AB test result --w=100

> ab -n 50000 -c 100 -r http://localhost/httptest/dir2/page.html
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests

Server Software: My-Agenirider-HTTP-server
Server Hostname: localhost
Server Port: 80

Document Path: /httptest/dir2/page.html
Document Length: 39 bytes

Concurrency Level: 100
Time taken for tests: 11.571 seconds
Complete requests: 50000
Failed requests: 1
(Connect: 0, Receive: 1, Length: 0, Exceptions: 0)
Total transferred: 9650000 bytes
HTML transferred: 1950000 bytes
Requests per second: 4321.23 [#/sec] (mean)
Time per request: 23.142 [ms] (mean)
Time per request: 0.231 [ms] (mean, across all concurrent requests)
Transfer rate: 814.45 [Kbytes/sec] received

Connection Times (ms)
min mean[+/-sd] median max
Connect: 0 1 0.7 1 15
Processing: 0 22 9.2 25 113
Waiting: 0 21 9.4 24 111
Total: 0 23 9.1 26 113

Percentage of the requests served within a certain time (ms)
50% 26
66% 27
75% 28
80% 29
90% 30
95% 39
98% 43
99% 55
100% 113 (longest request)