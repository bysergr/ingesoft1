export default function Footer() {
  return (
    <footer className={"border-t py-4 mt-6"}>
      <p className="text-center text-sm text-gray-500">
        © {new Date().getFullYear()} Naurat.
      </p>
    </footer>
  );
}
