import { Session } from "next-auth";
import Image from "next/image";

export const Profile = ({ session }: { session: Session }) => {
  const image = "https://placehold.co/60x60?text=USER&font=roboto";

  return (
    <div className="flex gap-4 items-center">
      <Image
        src={image}
        alt="Profile Picture"
        className="rounded-full"
        width={48}
        height={48}
      />
      <div className="">
        <p className="font-semibold">{session.user?.name || "user"}</p>
        <label className="text-xs text-neutral-400">
          {session.user?.email}
        </label>
      </div>
    </div>
  );
};
