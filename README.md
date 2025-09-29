# CliffINDUS
B2B and B2C Merger Program 

# Marketplace Platform (Manufacturer ⇄ Retailer ⇄ Consumer)

[![Build Status](https://img.shields.io/github/actions/workflow/status/your-org/your-repo/ci.yml?branch=main)](https://github.com/your-org/your-repo/actions)  

## 📖 Description

This project is a full-stack marketplace platform connecting **Manufacturers / Wholesalers → Retailers → Consumers**.  
- **B2B**: Manufacturers / Wholesalers publish products; retailers place bulk orders or request quotes.  
- **B2C**: Retailers list products to consumers; consumers browse, purchase, and the platform handles payments & commissions.

The goal is to enable flexible commerce workflows across roles, take platform commission, simplify payments, and provide a unified experience for all stakeholders.

## 🧩 Key Features (MVP)

- Role-based user accounts (Manufacturer, Retailer, Consumer, Admin)  
- Vendor onboarding flow & profile  
- Product catalog (CRUD, images, SKUs, inventory)  
- Retailer-to-manufacturer bulk ordering (quotas or order)  
- Consumer storefront: browse, cart, checkout  
- Payment & commission via Stripe Connect  
- Order management & basic notifications  
- Admin dashboard: user & transaction oversight  

## 📊 Tech Stack & Architecture

| Layer / Category        | Technology / Tool             | Purpose / Notes                              |
|--------------------------|-------------------------------|-----------------------------------------------|
| Frontend / UI            | Next.js + React + TypeScript   | Pages, API routes, SSR, client interactivity  |
| Styling / UI              | Tailwind CSS / CSS Modules     | Utility-first styling                         |
| State / Data Fetching     | React Query / SWR             | Cache & sync remote data in UI                |
| Backend / Server          | Node.js / Next.js API routes   | Server logic, endpoints                       |
| ORM / DB Access            | Prisma                         | Type-safe DB queries + migrations             |
| Database                 | PostgreSQL                     | Core relational data                          |
| Dev / Local Environment    | Docker + Docker Compose        | Isolate services (DB, etc.)                   |
| Authentication            | NextAuth.js / Auth.js           | Login, sessions, role-based access            |
| Payments / Marketplace     | Stripe + Stripe Connect         | Payment flow, vendor onboarding, payouts      |
| Testing (unit / integration) | Jest + React Testing Library  | Logic & component testing                     |
| E2E Testing                | Playwright or Cypress           | Full user-flow tests                           |
| CI / CD                    | GitHub Actions                   | Automated tests, build, deployment            |
| Hosting / Deployment       | Vercel (frontend + API routes)  | Deploy site + serverless handlers             |
| Monitoring / Errors         | Sentry                          | Runtime error tracking                        |
| Secrets & Config           | Environment variables / secret store | Store API keys, DB URLs, etc.        |
| (Optional) Caching / Jobs   | Redis / job queue                | For scaling & background tasks                 |
| (Optional) Asset Storage     | S3 / Cloud Storage               | Store images, files                            |

### Architecture Notes

- Use **Stripe Connect** in “platform mode” to onboard vendors and split payments (take commission)  
- Use **API routes** in Next.js for backend endpoints; move to microservices later if needed  
- Containerize with Docker for development parity  
- Use CI to validate test suite before deploying to production  

## 🛠️ Getting Started (Local Setup)

### Prerequisites

- Node.js (LTS)  
- Docker & Docker Compose  
- Git  
- GitHub account  
- Stripe account (for sandbox / test mode)  

### Installation & Setup

```bash
# 1. Clone the repo
git clone https://github.com/your-org/your-repo.git
cd your-repo

# 2. Copy environment file
cp .env.example .env
# Fill in variables: DATABASE_URL, NEXTAUTH_SECRET, STRIPE_*, etc.

# 3. Start local database & infrastructure
docker-compose up -d

# 4. Install dependencies
npm install

# 5. Run database migrations & (optionally) seed data
npx prisma migrate dev --name init
# (optional) npx prisma db seed

# 6. Start development server
npm run dev
