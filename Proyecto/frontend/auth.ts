import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

export const { handlers, signIn, signOut, auth } = NextAuth({
  session: {
    strategy: "jwt",
  },
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
  ],

  callbacks: {
    async jwt({ token, account, user }) {
      if (account?.provider === "google") {
        try {
          await fetch(
            `${process.env.NEXT_PUBLIC_BACKEND_URL}/ai/google-login/`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                email: user.email,
              }),
            },
          );
        } catch (error) {
          console.log({ error });
        }
      }

      return token;
    },
  },
  trustHost: true,
});
