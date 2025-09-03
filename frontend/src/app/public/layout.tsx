// This layout can be used to add a specific sidebar or header for the services section if needed.
// For now, it will just pass the children through.
export default function ServicesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <section>{children}</section>;
}