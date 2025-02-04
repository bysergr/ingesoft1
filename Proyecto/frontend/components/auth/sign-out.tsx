import { BsDoorOpenFill } from "react-icons/bs";
import { signOut } from "@/auth";

export function SignOut() {
  return (
    <form
      action={async () => {
        "use server";
        await signOut();
      }}
    >
      <button
        className="w-full flex gap-2 justify-center items-center py-2 rounded-md border-white border hover:bg-white hover:text-black transition"
        type="submit"
      >
        <BsDoorOpenFill type="" />
        Sign Out
      </button>
    </form>
  );
}
