import { auth, get } from '$lib/utils';

export async function load({ cookies, params, parent, url }) {
	let { user, subject } = await parent();
	let { pubkey } = subject;
	let { since = 0 } = params;

	let messages = [];

	if (user) {
		try {
			messages = await get(`/${user.pubkey}/${since}/messages`);
		} catch (e) {
			console.log(`failed to fetch nostr messages`, e);
		}
	}

	let notes = [];

	try {
		notes = await get(`/${pubkey}/notes`);
	} catch (e) {
		console.log(`failed to fetch nostr notes for ${pubkey}`, e);
	}

	notes.map((e) => {
		e.seen = e.created_at;
	});

	let { invoices, sent, received } = await get('/requests', auth(cookies));

	return { invoices, messages, notes, sent, received };
}
