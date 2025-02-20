import { fail, redirect } from '@sveltejs/kit';
import { auth, post } from '$lib/utils';

export async function load({ parent }) {
	let { user } = await parent();
	if (!user) throw redirect(307, '/register');
}

export const actions = {
	default: async ({ cookies, request }) => {
		let body = Object.fromEntries(await request.formData());

		try {
			await post('/take', body, auth(cookies));
		} catch (e) {
			return fail(400, { message: e.message });
		}

		throw redirect(307, `/pot/${body.name}`);
	}
};
