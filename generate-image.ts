#!/usr/bin/env npx tsx
/**
 * Gemini Image Generation (Nano Banana) - Beach Party Edition
 *
 * Usage:
 *   npx tsx generate-image.ts "your prompt"
 *   npx tsx generate-image.ts "your prompt" --count 4 --ratio 16:9
 *
 * Options:
 *   --count <number>   Number of images (1-4, default: 1)
 *   --ratio <string>   Aspect ratio (default: 16:9)
 *   --output <path>    Output directory (default: ./generated-images/)
 */

import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";
import * as path from "node:path";
import { config } from "dotenv";

// Load environment variables
config();

// Valid aspect ratios supported by Gemini
const VALID_ASPECT_RATIOS = [
  "1:1", "16:9", "9:16", "3:2", "2:3",
  "4:3", "3:4", "4:5", "5:4", "21:9"
];

interface Options {
  prompt: string;
  count: number;
  aspectRatio: string;
  outputDir: string;
  name: string;
}

function parseArgs(): Options {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error("Usage: npx tsx generate-image.ts \"your prompt\" [options]");
    process.exit(1);
  }

  const options: Options = {
    prompt: "",
    count: 1,
    aspectRatio: "16:9",
    outputDir: path.join(process.cwd(), "generated-images"),
    name: "",
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === "--count") {
      options.count = Math.min(4, Math.max(1, parseInt(args[++i]) || 1));
    } else if (arg === "--ratio") {
      const ratio = args[++i];
      if (VALID_ASPECT_RATIOS.includes(ratio)) {
        options.aspectRatio = ratio;
      }
    } else if (arg === "--output") {
      options.outputDir = args[++i];
    } else if (arg === "--name") {
      options.name = args[++i];
    } else if (!arg.startsWith("--")) {
      options.prompt = arg;
    }
  }

  if (!options.prompt) {
    console.error("Error: Prompt is required");
    process.exit(1);
  }

  return options;
}

async function generateImages(options: Options): Promise<string[]> {
  const apiKey = process.env.GEMINI_API_KEY;

  if (!apiKey) {
    throw new Error("GEMINI_API_KEY not found in .env file");
  }

  console.log(`\n🍌 Nano Banana Image Generation`);
  console.log(`📝 Prompt: "${options.prompt}"`);
  console.log(`🖼️  Aspect Ratio: ${options.aspectRatio}`);
  console.log(`#️⃣  Count: ${options.count}\n`);

  const ai = new GoogleGenAI({ apiKey });

  // Build prompt for multiple images
  let apiPrompt = options.prompt;
  if (options.count > 1) {
    apiPrompt = `Generate ${options.count} different variations of: ${options.prompt}`;
  }

  const result = await ai.models.generateContent({
    model: "gemini-3-pro-image-preview",
    contents: apiPrompt,
    config: {
      responseModalities: ["Text", "Image"],
      imageConfig: {
        aspectRatio: options.aspectRatio
      }
    }
  });

  // Ensure output directory exists
  const outputDir = path.resolve(options.outputDir);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    console.log(`📁 Created: ${outputDir}`);
  }

  const savedPaths: string[] = [];
  const timestamp = Date.now();

  // Extract images from response
  const parts = result.candidates?.[0]?.content?.parts || [];
  const imageParts = parts.filter((part: any) => part.inlineData?.mimeType?.startsWith("image/"));

  if (imageParts.length === 0) {
    // Check if there's text response
    const textParts = parts.filter((part: any) => part.text);
    if (textParts.length > 0) {
      console.log("\n📝 Model response:");
      textParts.forEach((part: any) => console.log(part.text));
    }
    throw new Error("No images were generated. The model may have refused or encountered an issue.");
  }

  console.log(`✅ Generated ${imageParts.length} image(s)\n`);

  for (let i = 0; i < imageParts.length; i++) {
    const imageData = imageParts[i].inlineData.data;
    const mimeType = imageParts[i].inlineData.mimeType;
    const ext = mimeType.includes("png") ? "png" : "jpg";
    const baseName = options.name || `beach-party-${timestamp}`;
    const filename = imageParts.length > 1 ? `${baseName}-${i + 1}.${ext}` : `${baseName}.${ext}`;
    const filepath = path.join(outputDir, filename);

    const buffer = Buffer.from(imageData, "base64");
    fs.writeFileSync(filepath, buffer);

    savedPaths.push(filepath);
    console.log(`💾 Saved: ${path.relative(process.cwd(), filepath)}`);
  }

  return savedPaths;
}

async function main() {
  try {
    const options = parseArgs();
    const savedPaths = await generateImages(options);

    console.log(`\n✨ Success! Generated ${savedPaths.length} image(s)`);
  } catch (error) {
    console.error("\n❌ Error:", error instanceof Error ? error.message : String(error));

    if (error instanceof Error && error.message.includes("GEMINI_API_KEY")) {
      console.error("\n💡 Create .env file with: GEMINI_API_KEY=your_key_here");
      console.error("   Get key at: https://aistudio.google.com/apikey");
    }

    process.exit(1);
  }
}

main();
