import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppProvider } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "HireUs - AI-Powered Hiring Platform",
  description: "Structured technical interview platform with hiring intelligence for founders",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppProvider>
          <div className="min-h-screen bg-background">
            <main>{children}</main>
          </div>
        </AppProvider>
      </body>
    </html>
  );
}

