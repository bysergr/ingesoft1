import { AsideLeft, AsideRight } from "@/components/aside";
import { Chat } from "@/components/chat";
import Footer from "@/components/footer";

export default function Home() {
  return (
    <div className="h-screen flex">
      <AsideLeft />
      <div className="h-full flex-grow flex-shrink">
        <Chat email={undefined} name={undefined} />
        <Footer />
      </div>
      <AsideRight />
    </div>
  );
}
