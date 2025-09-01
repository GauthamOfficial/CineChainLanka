# CineChainLanka 🎬

A blockchain-powered decentralized platform designed to transform film and content funding in Sri Lanka by enabling creators to raise funds transparently using smart contracts, NFTs, and automated royalty distribution.

## 🚀 Project Status

**Phase 1: Foundation & MVP Development** - ✅ **COMPLETED**

## ✨ Features

### Phase 1 (Completed)
- ✅ **User Management & Authentication**
  - User registration with email verification
  - JWT-based authentication system
  - User profile management
  - Role-based access control (Creator, Investor, Admin)

- ✅ **Campaign Management System**
  - Campaign creation and management
  - Campaign categories and status tracking
  - Funding goal and deadline management
  - Campaign analytics and metrics

- ✅ **KYC Integration**
  - KYC verification workflow
  - Document upload functionality
  - Compliance checks integration

- ✅ **Payment System**
  - Local payment methods (LankaQR, eZ Cash, FriMi)
  - Transaction management and tracking
  - Payment status monitoring

- ✅ **Modern Web Interface**
  - Responsive React frontend with Tailwind CSS
  - Redux state management
  - Multi-language support ready (Sinhala, Tamil, English)
  - User dashboards for creators and backers

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.2.5
- **Database**: MySQL (with SQLite fallback for development)
- **Authentication**: JWT with Simple JWT
- **API**: Django REST Framework
- **File Storage**: Local file system (ready for IPFS integration)
- **Caching**: Redis ready

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Redux Toolkit
- **Routing**: React Router v6
- **UI Components**: Headless UI + Heroicons
- **HTTP Client**: Axios with interceptors

### Blockchain Ready
- **Web3 Integration**: Web3.py
- **Smart Contracts**: Solidity ready
- **Blockchain**: Ethereum/Polygon ready

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL (optional, SQLite will be used by default)
- Redis (optional)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CineChainLanka
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .cinechain
   source .cinechain/bin/activate  # On Windows: .cinechain\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create sample data**
   ```bash
   python manage.py populate_sample_data
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

## 🔐 Demo Credentials

For testing purposes, use these sample credentials:

- **Admin User**: `admin_user` / `testpass123`
- **Creator User**: `creator1` / `testpass123`
- **Investor User**: `investor1` / `testpass123`

## 📱 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh/` - Token refresh

### Users
- `GET /api/users/profile/` - Get user profile
- `PATCH /api/users/profile/` - Update user profile

### Campaigns
- `GET /api/campaigns/` - List campaigns
- `POST /api/campaigns/` - Create campaign
- `GET /api/campaigns/{id}/` - Get campaign details
- `PATCH /api/campaigns/{id}/` - Update campaign

### Payments
- `GET /api/payments/methods/` - List payment methods
- `GET /api/payments/transactions/` - List transactions
- `POST /api/payments/transactions/` - Create transaction

### KYC
- `GET /api/kyc/requests/` - List KYC requests
- `POST /api/kyc/requests/` - Submit KYC request

## 🏗️ Project Structure

```
CineChainLanka/
├── campaigns/          # Campaign management app
├── funding/            # Funding and investment app
├── kyc/               # KYC verification app
├── payments/          # Payment processing app
├── users/             # User management app
├── cinechain_backend/ # Django project settings
├── frontend/          # React frontend application
├── static/            # Static files
├── media/             # User uploaded files
├── templates/         # Django templates
└── requirements.txt   # Python dependencies
```

## 🌐 Multi-language Support

The platform is configured to support:
- **English** (en-us) - Primary language
- **Sinhala** (si) - Local language
- **Tamil** (ta) - Local language

## 🔒 Security Features

- JWT authentication with refresh tokens
- Password validation and hashing
- CORS configuration
- File upload validation
- KYC verification workflow
- Role-based access control

## 📊 Database Schema

The platform includes comprehensive models for:
- **Users**: Extended user model with KYC and verification
- **Campaigns**: Full campaign lifecycle management
- **Payments**: Transaction tracking and payment methods
- **KYC**: Document verification and compliance

## 🚧 Development Roadmap

### Phase 2: Blockchain Integration & NFT System (Q1 2026)
- Smart contract development
- Wallet integration (MetaMask, TrustWallet)
- NFT minting and management
- IPFS storage integration
- Crypto payment processing

### Phase 3: Royalty System & Advanced Features (Q2 2026)
- Automated royalty distribution
- Advanced analytics dashboards
- Mobile application (React Native)
- NFT marketplace functionality

### Phase 4: Scale & Global Expansion (Q3 2026)
- Performance optimization
- Global partnerships
- AI integration
- Advanced security features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🙏 Acknowledgments

- Django community for the excellent web framework
- React team for the powerful frontend library
- Tailwind CSS for the utility-first CSS framework
- All contributors and supporters of the project

---

**Made with ❤️ in Sri Lanka**

