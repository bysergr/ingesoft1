import Image from "next/image";
import { auth } from "@/auth";
import { SignIn } from "@/components/auth/sign-in";
import { Profile } from "@/components/auth/profile";
import { SignOut } from "@/components/auth/sign-out";

export const AsideRight = async () => {
  return (
    <aside className="px-6 w-[262px] flex-shrink-0 flex-grow-0 h-full hidden md:flex flex-col justify-around border-l-neutral-600 border-l">
      <div className="w-full">
        <h3 className="font-bold text-xl">Ingesoft Project</h3>
        <Image
          src="/unal.svg"
          alt="Expert"
          width={230}
          height={230}
          className="mx-auto mt-3"
        />
        <div className="ml-2 mt-8 space-y-4">
          <p>
            This product was designed and developed for the{" "}
            <strong> Software Engineering 1 </strong> course, exclusively for
            educational purposes. Therefore, its commercialization and
            distribution are strictly prohibited.
          </p>
          <p>
            <strong> Talk to our import expert </strong>
          </p>
          <p>
            If you need to speak with a specialist in importing and exporting
            goods to Mexico, you can contact our expert. Schedule a meeting
            using the following link.
          </p>
          <a
            className="w-11/12 block text-center py-2 rounded-md font-semibold border border-[#8B42FF] bg-[#8B42FF] hover:bg-transparent text-white hover:text-[#8B42FF] transition"
            href="https://calendly.com/joaquintally/30min?month=2025-01"
            target="_blank"
            rel="noopener noreferrer"
          >
            Calendly
          </a>
        </div>
      </div>
      <div className=""></div>
    </aside>
  );
};

export async function AsideLeft() {
  const session = await auth();

  return (
    <aside className="px-6 w-[262px] text-white bg-black flex-shrink-0 flex-grow-0 h-full hidden md:flex flex-col justify-around border-r-neutral-600 border-r">
      <div className="w-full">
        <a
          className="flex items-end mx-auto w-fit mb-8"
          href="https://www.naurat.com/"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image src="/favicon.ico" alt="Naurat logo" width={90} height={90} />
        </a>

        <h3 className="font-bold text-2xl">
          Want to keep a record of all the products you look for?
        </h3>
        <div className="ml-2 mt-8 space-y-4">
          <p>
            Use the import Bot to find products and evaluate their costs and
            requirements. Log in first to download the list in Excel, including
            your selected products and details.
          </p>
          {session && <button>Download Sheet</button>}
        </div>

        <div className="h-36 flex flex-col justify-center mt-12">
          {session ? (
            <div className="space-y-6">
              <Profile session={session} />
              <SignOut />
            </div>
          ) : (
            <SignIn />
          )}
          <p className="text-xs text-neutral-300 mt-6 text-center">
            Made with 🤍 by our software developer expert{" "}
            <a
              href="https://github.com/FabianEspitia-it"
              target="_blank"
              rel="noopener noreferrer"
              className="underline text-white"
            >
              Fabian Espitia
            </a>
            .
          </p>
        </div>
      </div>

      <div className=""></div>
    </aside>
  );
}
