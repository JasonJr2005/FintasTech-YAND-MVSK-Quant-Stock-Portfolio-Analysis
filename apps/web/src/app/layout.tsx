import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FintasTech YAND-MVSK",
  description: "A higher-moment quantitative research platform powered by YAND-MVSK.",
  icons: {
    icon: "/fintastech-logo.svg"
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
