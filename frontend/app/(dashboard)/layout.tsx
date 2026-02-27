"use client";

import React from "react";
import DashboardLayout from "@/components/layout/dashboard-layout";

interface DashboardGroupLayoutProps {
  children: React.ReactNode;
}

export default function DashboardGroupLayout({ children }: DashboardGroupLayoutProps) {
  return <DashboardLayout>{children}</DashboardLayout>;
}

