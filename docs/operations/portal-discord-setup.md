# Setting up the Discord side of the portal

Written for the Operations Owner. No technical background assumed. About fifteen
minutes. Nothing here touches the live Freedom Blades community — everything is
done in the **test** server and the **test** application.

You need four values at the end. Write them on paper or in your password
manager; three are harmless identifiers, **one is a secret** and is marked.

---

## 1. Turn on Developer Mode (once)

Discord hides the ID numbers until you ask for them.

In the Discord app: **User Settings** (the cog, bottom left) → **Advanced** →
switch on **Developer Mode**.

You can now right-click almost anything and get "Copy ID".

## 2. Create three roles in the test server

In the **Freedom-Blades Test** server: **Server Settings** → **Roles** → **Create Role**.
Make three, exactly these purposes (the names are yours to choose — the system
uses the ID, never the name):

| Role | What it will mean |
|---|---|
| Guild Council | approves character links and applies imports |
| DM | prepares missions; no approval authority in Phase 3 |
| Platform Administrator | server administration only — never game decisions |

**Give all three to yourself**, so you can test what each one sees.

Then right-click each role → **Copy ID**, and note them as *Council ID*, *DM ID*
and *Administrator ID*.

## 3. Copy the server ID

Right-click the **Freedom-Blades Test** server name → **Copy ID**. Note it as
*Server ID*.

## 4. Add the sign-in address to the application

Go to <https://discord.com/developers/applications> and open your
**Freedom-Blades Test** application.

1. Left menu → **OAuth2**.
2. Under **Redirects**, click **Add Redirect** and paste exactly:

   ```
   https://freedom-blades.rpgworld.org/auth/discord/callback
   ```

   It must match character for character, including `https://` and no trailing
   slash. Discord refuses anything that does not match exactly, and so do we.
3. **Save Changes** at the bottom.

## 5. Copy the two application values

Still on the same page:

- **Client ID** — a long number. Copy it. Not secret.
- **Client Secret** — click **Reset Secret** if no value is shown, then copy it.

> **The Client Secret is a password.** Do not paste it into a chat, a document,
> an email or a note that syncs anywhere. It goes straight into one file on the
> server, in step 7. If it ever leaks, come back here and press **Reset Secret** —
> that immediately invalidates the old one.

## 6. Invite the bot to the test server

Left menu → **Installation** (or **OAuth2 → URL Generator**), generate an invite
for the **bot** scope, open the link, and add it to **Freedom-Blades Test**.

It needs no permissions to do anything. This is belt-and-braces: it removes a
whole class of "why can't it see my roles" problem later.

## 7. Put the four values on the server

Open the configuration file:

```
sudo nano /etc/freedom-blades/portal.env
```

Find these four lines and replace the `__FILL_IN...__` text after the `=` with
your values. No quotes, no spaces around the `=`:

```
WEB_DISCORD_CLIENT_ID=<Client ID from step 5>
WEB_DISCORD_CLIENT_SECRET=<Client Secret from step 5>
WEB_DISCORD_GUILD_ID=<Server ID from step 3>
WEB_BOOTSTRAP_ADMIN_ROLE_ID=<Administrator ID from step 2>
```

Save with **Ctrl-O**, **Enter**, then exit with **Ctrl-X**.

The Council and DM role IDs are **not** put in this file — they are set up inside
the portal afterwards. Just keep them to hand.

## 8. Tell Claude

Send the *Council ID*, *DM ID*, *Administrator ID* and *Server ID*. **Never send
the Client Secret** — it is already where it needs to be and nowhere else.

---

## If something goes wrong

**"Invalid OAuth2 redirect_uri" when signing in** — step 4's address does not
match exactly. Compare it character by character; a trailing slash is the usual
culprit.

**The portal refuses to start** — it does that on purpose while any value still
contains `__`. It will tell you which one in its log.

**You pasted the secret somewhere by accident** — press **Reset Secret** in the
developer portal, then redo step 7 with the new value. No other cleanup needed.
