import { randomIntBetween, sleep } from "k6";
import http from "k6/http";

export let options = {
	vus: 50, // max users
	duration: "1h", // run for 1 hour
};

export default function () {
	// Each VU acts randomly: sleeps and sends requests at random intervals
	let shouldRequest = Math.random() < 0.6; // ~60% chance to send request

	if (shouldRequest) {
		let payload = JSON.stringify("ABCDEDGHIJKLMNOP");
		let headers = { "Content-Type": "application/json" };
		http.post("http://192.168.49.102/hash/sha256", payload, { headers });
	}

	sleep(randomIntBetween(1, 5)); // 1 to 5 seconds delay
}
