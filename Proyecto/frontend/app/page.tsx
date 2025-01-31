import { Aside } from "@/components/aside";
import { Chat } from "@/components/chat";
import Footer from "@/components/footer";

export default function Home() {
  return (
    <div className="h-screen flex">
      <Aside />
      <div className="h-full flex-grow flex-shrink">
        <Chat email={undefined} name={undefined} />
        <Footer />
      </div>
    </div>
  );
}
