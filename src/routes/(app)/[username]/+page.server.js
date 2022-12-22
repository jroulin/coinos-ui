import { get } from '$lib/utils';
import Qr from 'qrcode-base64';

export async function load({ params, parent, url }) {
	let { subject } = await parent();
	let { pubkey } = subject;
	if (!pubkey) pubkey = params.username;

	let { username } = params;
	let text = `${encodeURI(username)}@${url.hostname}`;
	let src = Qr.drawImg(text, { size: 300 });
	let events = [];

	try {
		events = await get(`/${pubkey}/events`);
	} catch (e) {
		console.log(e);
	}

	events.map((e) => {
		e.seen = e.created_at;
	});

	return { events, src, text };
}
