import { FcGoogle } from "react-icons/fc";
import { signIn } from "@/auth";

export function SignIn() {
  return (
    <form
      action={async () => {
        "use server";
        await signIn("google");
      }}
    >
      <button className="w-full flex gap-2 justify-center items-center font-semibold py-2 rounded-md bg-black text-white border border-white hover:bg-white hover:text-black  transition">
        <FcGoogle />
        Sign In
      </button>
    </form>
  );
}
