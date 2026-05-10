$ErrorActionPreference = "Stop"
Push-Location .\frontend
npm install
npx playwright install chromium
npm run test:e2e
Pop-Location
