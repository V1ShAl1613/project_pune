import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 25 },
    { duration: '10m', target: 25 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.02'],
    http_req_duration: ['p(95)<1000'],
  },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL || 'http://localhost:8000'}/api/v1/executive/overview`);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
