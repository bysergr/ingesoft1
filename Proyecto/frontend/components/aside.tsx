import Image from "next/image";
import { auth } from "@/auth";

export async function Aside() {
  const session = await auth();

  return (
    <aside className="px-6 w-[282px] text-white bg-black flex-shrink-0 flex-grow-0 h-full hidden md:flex flex-col justify-around border-r-neutral-600 border-r">
      <div className="w-full">
        <a
          className="flex items-end mx-auto w-fit mb-8"
          href="https://www.naurat.com/"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            src="https://naurat.com/favicon.ico"
            alt="Naurat logo"
            width={50}
            height={30}
          />
          <label className="font-semibold text-4xl cursor-pointer -translate-x-1">
            aurat
          </label>
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
          {session ? <div className="space-y-6">Sign out</div> : <p>Sign In</p>}
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
