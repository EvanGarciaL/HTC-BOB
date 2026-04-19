import { NextRequest, NextResponse } from "next/server";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import path from "node:path";

const execFileAsync = promisify(execFile);

export async function GET(request: NextRequest) {
  const term = request.nextUrl.searchParams.get("term") || "";
  const category = request.nextUrl.searchParams.get("category") || "uncategorized";

  if (!term) {
    return NextResponse.json(
      { error: "Missing term", competitors: [], recommendations: [] },
      { status: 400 },
    );
  }

  try {
    const scriptPath = path.resolve(process.cwd(), "../fetch_product_insights.py");
    const pythonCommand = process.env.PYTHON || (process.platform === "win32" ? "python" : "python3");
    const { stdout } = await execFileAsync(pythonCommand, [scriptPath, term, category], {
      cwd: process.cwd(),
      timeout: 60000,
      maxBuffer: 1024 * 1024,
    });
    const payload = JSON.parse(stdout);
    return NextResponse.json(payload);
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Unable to fetch product insights.",
        competitors: [],
        recommendations: [],
      },
      { status: 500 },
    );
  }
}
