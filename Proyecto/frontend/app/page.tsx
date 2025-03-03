import { AsideLeft, AsideRight } from "@/components/aside";
import { Chat } from "@/components/chat";
import Footer from "@/components/footer";
import { auth } from "@/auth";

export default async function Home() {
  const session = await auth();

  const email = session?.user?.email;
  const name = session?.user?.name;

  return (
    <div className="h-screen flex">
      <AsideLeft />
      <div className="h-full flex-grow flex-shrink">
        <Chat email={email || undefined} name={name || undefined} />
        <Footer />
      </div>
      <AsideRight />
    </div>
  );
}
