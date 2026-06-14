# 🧠 Skill for Manus AI — Intelligence & Credit Optimizer

Koleksi skill komprehensif untuk meningkatkan kecerdasan dan kemampuan Manus AI, dilengkapi dengan sistem penghematan credit yang cerdas.

## 📋 Daftar Skill

### 💰 Credit Saver (Penghematan Credit)
| Skill | Deskripsi | Estimasi Hemat |
|-------|-----------|----------------|
| `token-optimizer` | Kompresi prompt & respons untuk hemat token | 30-50% |
| `smart-routing` | Routing cerdas ke model yang tepat sesuai kompleksitas | 40-60% |
| `cache-manager` | Caching hasil untuk menghindari request berulang | 50-80% |
| `batch-processor` | Menggabungkan request kecil jadi satu batch besar | 25-40% |
| `context-pruner` | Memangkas konteks yang tidak relevan | 20-35% |
| `incremental-solver` | Memecah masalah besar jadi langkah kecil yang hemat | 30-45% |

### 💻 Coding
| Skill | Deskripsi |
|-------|-----------|
| `code-review` | Review kode otomatis dengan standar industri |
| `debugging` | Debugging cerdas dengan root cause analysis |
| `refactoring` | Refactoring kode untuk kualitas & performa |
| `testing` | Generasi test otomatis (unit, integration, e2e) |
| `architecture` | Desain arsitektur sistem & pattern |
| `code-generation` | Generasi kode dari spesifikasi natural language |
| `performance-optimizer` | Optimasi performa kode & query |

### 🔍 Research
| Skill | Deskripsi |
|-------|-----------|
| `web-research` | Riset web mendalam & terstruktur |
| `data-analysis` | Analisis data dengan insight actionable |
| `summarization` | Ringkasan dokumen & paper cerdas |
| `competitive-analysis` | Analisis kompetitor & market |
| `trend-analysis` | Analisis tren teknologi & industri |

### ✍️ Writing
| Skill | Deskripsi |
|-------|-----------|
| `technical-writing` | Dokumentasi teknis profesional |
| `copywriting` | Copywriting persuasif & engaging |
| `translation` | Terjemahan multi-bahasa berkualitas |
| `content-strategy` | Strategi konten & editorial planning |
| `seo-writing` | Penulisan SEO-optimized |

### ⚙️ Automation
| Skill | Deskripsi |
|-------|-----------|
| `ci-cd` | Setup & optimasi CI/CD pipeline |
| `deployment` | Deployment otomatis multi-platform |
| `monitoring` | Setup monitoring & alerting |
| `scripting` | Otomasi scripting (Bash, PowerShell, Python) |
| `workflow-builder` | Pembuatan workflow otomasi kustom |

### 📊 Data
| Skill | Deskripsi |
|-------|-----------|
| `etl-pipeline` | Pembuatan ETL pipeline |
| `visualization` | Visualisasi data & dashboard |
| `data-cleaning` | Pembersihan & normalisasi data |
| `migration` | Migrasi data antar sistem |
| `database-optimizer` | Optimasi database & query |

### 🔒 Security
| Skill | Deskripsi |
|-------|-----------|
| `security-audit` | Audit keamanan kode & infrastruktur |
| `vulnerability-scan` | Scanning kerentanan otomatis |
| `hardening` | Hardening sistem & konfigurasi |
| `compliance-check` | Pemeriksaan compliance (OWASP, SOC2, dll) |
| `incident-response` | Panduan respons insiden keamanan |

### 🚀 DevOps
| Skill | Deskripsi |
|-------|-----------|
| `docker` | Manajemen Docker & containerization |
| `kubernetes` | Orchestrasi Kubernetes |
| `infrastructure` | Infrastructure as Code (Terraform, Pulumi) |
| `cloud-architect` | Arsitektur cloud multi-provider |
| `cost-optimizer` | Optimasi biaya cloud |

### 📈 Productivity
| Skill | Deskripsi |
|-------|-----------|
| `project-planning` | Perencanaan proyek & sprint |
| `documentation` | Generasi dokumentasi otomatis |
| `meeting-assistant` | Asisten meeting & notulen |
| `task-decomposer` | Dekomposisi task kompleks |
| `knowledge-base` | Pembangunan knowledge base |

### 🎨 Creative
| Skill | Deskripsi |
|-------|-----------|
| `brainstorming` | Brainstorming ide terstruktur |
| `ui-design` | Desain UI/UX dengan best practices |
| `prototyping` | Rapid prototyping |
| `naming-convention` | Penamaan project, brand, variabel |
| `pitch-deck` | Pembuatan pitch deck & presentasi |

## 🏗️ Arsitektur

```
skill-for-manus-ai/
├── core/
│   ├── __init__.py          # Package init
│   ├── loader.py            # Skill loader & registry
│   ├── credit_manager.py    # Credit management & tracking
│   ├── router.py            # Smart skill routing
│   └── config.py            # Global configuration
├── skills/
│   ├── credit-saver/        # 6 skill penghematan credit
│   ├── coding/              # 7 skill coding
│   ├── research/            # 5 skill riset
│   ├── writing/             # 5 skill penulisan
│   ├── automation/          # 5 skill otomasi
│   ├── data/                # 5 skill data
│   ├── security/            # 5 skill keamanan
│   ├── devops/              # 5 skill devops
│   ├── productivity/        # 5 skill produktivitas
│   └── creative/            # 5 skill kreativitas
├── requirements.txt
├── setup.py
└── README.md
```

## 🚀 Penggunaan

### Instalasi
```bash
pip install -e .
```

### Quick Start
```python
from core.loader import SkillRegistry
from core.credit_manager import CreditManager

# Inisialisasi
registry = SkillRegistry()
credit_mgr = CreditManager(daily_limit=1500)

# Load semua skill
registry.load_all()

# Jalankan skill dengan credit tracking
result = registry.execute(
    skill_name="code-review",
    context={"code": "def hello(): print('world')"},
    credit_manager=credit_mgr
)

# Cek sisa credit
print(f"Credit tersisa: {credit_mgr.remaining}")
print(f"Credit dihemat: {credit_mgr.total_saved}")
```

### Credit-Aware Execution
```python
from core.router import SmartRouter

router = SmartRouter(credit_manager=credit_mgr)

# Router otomatis pilih strategi paling hemat
result = router.route(
    task="Review this Python function for bugs",
    context={"code": source_code},
    max_credit=50  # batas credit per task
)
```

## 📊 Statistik Penghematan

Dengan menggunakan semua fitur credit-saver:

| Skenario | Tanpa Optimasi | Dengan Optimasi | Hemat |
|----------|---------------|-----------------|-------|
| Code Review 100 files | ~3000 credit | ~1200 credit | 60% |
| Research + Summary | ~500 credit | ~200 credit | 60% |
| Batch Translation | ~1000 credit | ~350 credit | 65% |
| Daily Coding Assist | ~1500 credit | ~600 credit | 60% |

## 📄 Lisensi

MIT License — lihat [LICENSE](LICENSE) untuk detail.
