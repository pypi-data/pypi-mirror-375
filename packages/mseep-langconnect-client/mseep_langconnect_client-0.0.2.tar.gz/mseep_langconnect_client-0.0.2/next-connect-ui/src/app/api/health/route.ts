import { NextResponse } from "next/server"
import { serverFetchAPI } from "@/lib/api"

export async function GET(request: Request) {
  try {
    // 백엔드 API 호출
    const response = await serverFetchAPI("/health", {
      method: "GET",
    })

    return NextResponse.json({ success: true, data: response }, { status: 201 })
  } catch (error: any) {
    return NextResponse.json({ message: error.message }, { status: 500 })
  }
}