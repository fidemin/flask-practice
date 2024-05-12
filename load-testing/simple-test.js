import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '60s',
};

export default function () {
  http.get('http://127.0.0.1/api/employees/1');
  sleep(0.1);
}