import { useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  Boxes,
  Building2,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleDollarSign,
  ClipboardList,
  Clock3,
  Download,
  FileText,
  Filter,
  History,
  LayoutDashboard,
  LocateFixed,
  LogOut,
  Map,
  MapPin,
  Menu,
  Minus,
  MoreHorizontal,
  Navigation,
  Package,
  PackageCheck,
  PackageOpen,
  Pencil,
  Plus,
  QrCode,
  Search,
  Settings,
  ShoppingBag,
  ShoppingCart,
  Sparkles,
  Store,
  Truck,
  UserRound,
  Users,
  Warehouse,
  X,
  XCircle,
  type LucideIcon,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type AppMode = "supplier" | "admin" | "partner" | "shipper";
type OrderStatus = "Chờ duyệt" | "Đã duyệt" | "Đang giao" | "Hoàn thành" | "Đã hủy";
type Order = {
  id: string;
  dealer: string;
  items: number;
  total: number;
  status: OrderStatus;
  date: string;
  address: string;
};

type SupplyStatus =
  | "Chờ phản hồi"
  | "Đã xác nhận"
  | "Đang vận chuyển"
  | "Đã nhập kho"
  | "Đã từ chối";
type SupplyRequest = {
  id: string;
  product: string;
  sku: string;
  qty: number;
  due: string;
  warehouse: string;
  value: number;
  status: SupplyStatus;
};

const productPhotos = [
  "https://images.unsplash.com/photo-1627915589334-14a3c3e3a741?auto=format&fit=crop&w=640&q=80",
  "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=640&q=80",
  "https://images.unsplash.com/photo-1684695749267-233af13276d0?auto=format&fit=crop&w=640&q=80",
];

const products = [
  {
    id: 1,
    name: "Nước khoáng Lavie 500ml",
    sku: "LV-500-24",
    price: 118000,
    stock: 1240,
    image: productPhotos[0],
    category: "Đồ uống",
  },
  {
    id: 2,
    name: "Thùng sữa TH True Milk",
    sku: "TH-180-48",
    price: 348000,
    stock: 386,
    image: productPhotos[1],
    category: "Sữa & dinh dưỡng",
  },
  {
    id: 3,
    name: "Dầu ăn Simply 1L",
    sku: "SMP-1L-12",
    price: 612000,
    stock: 92,
    image: productPhotos[2],
    category: "Thực phẩm",
  },
  {
    id: 4,
    name: "Cà phê Trung Nguyên S",
    sku: "TN-S-500",
    price: 89000,
    stock: 640,
    image: productPhotos[0],
    category: "Đồ uống",
  },
  {
    id: 5,
    name: "Bánh quy Cosy Marie",
    sku: "CS-MR-20",
    price: 236000,
    stock: 24,
    image: productPhotos[1],
    category: "Bánh kẹo",
  },
  {
    id: 6,
    name: "Nước giặt OMO Matic",
    sku: "OMO-3.9",
    price: 186000,
    stock: 218,
    image: productPhotos[2],
    category: "Hàng gia dụng",
  },
];

const chartData = [
  { day: "01/06", nhap: 160, xuat: 118 },
  { day: "05/06", nhap: 210, xuat: 165 },
  { day: "09/06", nhap: 178, xuat: 192 },
  { day: "13/06", nhap: 260, xuat: 205 },
  { day: "17/06", nhap: 238, xuat: 228 },
  { day: "21/06", nhap: 290, xuat: 245 },
  { day: "25/06", nhap: 268, xuat: 278 },
  { day: "29/06", nhap: 330, xuat: 296 },
];

const initialOrders: Order[] = [
  {
    id: "DH-240628",
    dealer: "Đại lý Minh Phát",
    items: 8,
    total: 18640000,
    status: "Chờ duyệt",
    date: "28/06/2025",
    address: "128 Nguyễn Văn Linh, Q.7, TP.HCM",
  },
  {
    id: "DH-240627",
    dealer: "Siêu thị An Nhiên",
    items: 12,
    total: 24780000,
    status: "Đã duyệt",
    date: "27/06/2025",
    address: "42 Lê Văn Việt, TP. Thủ Đức",
  },
  {
    id: "DH-240626",
    dealer: "Tạp hóa Thành Công",
    items: 5,
    total: 8920000,
    status: "Đang giao",
    date: "26/06/2025",
    address: "16 Nguyễn Oanh, Gò Vấp, TP.HCM",
  },
  {
    id: "DH-240625",
    dealer: "Mart 365 Bình Thạnh",
    items: 16,
    total: 32160000,
    status: "Hoàn thành",
    date: "25/06/2025",
    address: "220 Xô Viết Nghệ Tĩnh, Bình Thạnh",
  },
  {
    id: "DH-240624",
    dealer: "Đại lý Phúc Khang",
    items: 3,
    total: 5240000,
    status: "Đã hủy",
    date: "24/06/2025",
    address: "78 Trường Chinh, Tân Bình, TP.HCM",
  },
];

const initialSupplyRequests: SupplyRequest[] = [
  {
    id: "NK-250629",
    product: "Nước khoáng Lavie 500ml",
    sku: "LV-500-24",
    qty: 1200,
    due: "03/07/2025",
    warehouse: "Kho trung tâm A • Quận 7",
    value: 141600000,
    status: "Chờ phản hồi",
  },
  {
    id: "NK-250626",
    product: "Cà phê Trung Nguyên S",
    sku: "TN-S-500",
    qty: 480,
    due: "05/07/2025",
    warehouse: "Kho trung chuyển C • Bình Chánh",
    value: 42720000,
    status: "Đã xác nhận",
  },
  {
    id: "NK-250621",
    product: "Thùng sữa TH True Milk",
    sku: "TH-180-48",
    qty: 320,
    due: "29/06/2025",
    warehouse: "Kho lạnh B2 • TP. Thủ Đức",
    value: 111360000,
    status: "Đang vận chuyển",
  },
  {
    id: "NK-250614",
    product: "Dầu ăn Simply 1L",
    sku: "SMP-1L-12",
    qty: 150,
    due: "20/06/2025",
    warehouse: "Kho trung tâm A • Quận 7",
    value: 91800000,
    status: "Đã nhập kho",
  },
];

const formatMoney = (value: number) =>
  new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(value);

const statusStyle: Record<OrderStatus, string> = {
  "Chờ duyệt": "bg-amber-50 text-amber-700 ring-amber-200",
  "Đã duyệt": "bg-blue-50 text-blue-700 ring-blue-200",
  "Đang giao": "bg-orange-50 text-orange-700 ring-orange-200",
  "Hoàn thành": "bg-emerald-50 text-emerald-700 ring-emerald-200",
  "Đã hủy": "bg-slate-100 text-slate-500 ring-slate-200",
};

function Status({ value }: { value: OrderStatus }) {
  return (
    <span
      className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1 ring-inset ${statusStyle[value]}`}
    >
      {value}
    </span>
  );
}

function Logo({ compact = false, dark = false }: { compact?: boolean; dark?: boolean }) {
  return (
    <div className="flex items-center gap-2.5">
      <div className="grid size-9 shrink-0 place-items-center rounded-xl bg-blue-600 shadow-lg shadow-blue-600/25">
        <div className="relative size-4">
          <span className="absolute left-0 top-0 h-1.5 w-4 rounded-sm bg-white" />
          <span className="absolute left-0 top-[7px] h-1.5 w-3 rounded-sm bg-white/85" />
          <span className="absolute left-0 top-[14px] h-1.5 w-2 rounded-sm bg-white/60" />
        </div>
      </div>
      {!compact && (
        <div>
          <div
            className={`text-[15px] font-extrabold tracking-[.08em] ${dark ? "text-white" : "text-slate-900"}`}
          >
            DISTRIFLOW
          </div>
          <div
            className={`text-[9px] font-medium tracking-[.12em] ${dark ? "text-slate-400" : "text-slate-400"}`}
          >
            DISTRIBUTION OS
          </div>
        </div>
      )}
    </div>
  );
}

function DemoSwitcher({ mode, setMode }: { mode: AppMode; setMode: (m: AppMode) => void }) {
  const entries: {
    id: AppMode;
    label: string;
    icon: LucideIcon;
    color: string;
    active: string;
  }[] = [
    {
      id: "supplier",
      label: "Nhà cung cấp",
      icon: Building2,
      color: "text-violet-600",
      active: "bg-violet-600 text-white shadow-violet-600/25",
    },
    {
      id: "admin",
      label: "Quản lý kho",
      icon: Warehouse,
      color: "text-blue-600",
      active: "bg-blue-600 text-white shadow-blue-600/25",
    },
    {
      id: "partner",
      label: "Đại lý",
      icon: Store,
      color: "text-emerald-600",
      active: "bg-emerald-600 text-white shadow-emerald-600/25",
    },
    {
      id: "shipper",
      label: "Shipper",
      icon: Truck,
      color: "text-orange-600",
      active: "bg-orange-600 text-white shadow-orange-600/25",
    },
  ];
  return (
    <div className="demo-switcher">
      <span className="hidden text-[10px] font-bold uppercase tracking-[.14em] text-slate-400 sm:block">
        Chế độ xem
      </span>
      <div className="flex rounded-xl border border-slate-200 bg-white p-1 shadow-lg shadow-slate-900/8">
        {entries.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => setMode(item.id)}
              className={`switcher-button ${mode === item.id ? `${item.active} shadow-lg` : "text-slate-500 hover:bg-slate-50"}`}
            >
              <Icon size={14} className={mode === item.id ? "text-white" : item.color} />
              {item.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Toast({ message }: { message: string }) {
  return (
    <div className="fixed right-4 top-20 z-[80] flex max-w-[calc(100%-2rem)] items-center gap-3 rounded-xl border border-emerald-200 bg-white px-4 py-3 shadow-2xl shadow-slate-900/15">
      <span className="grid size-7 place-items-center rounded-full bg-emerald-50 text-emerald-600">
        <Check size={16} strokeWidth={3} />
      </span>
      <p className="text-sm font-semibold text-slate-700">{message}</p>
    </div>
  );
}

const adminNav: [string, LucideIcon][] = [
  ["Tổng quan", LayoutDashboard],
  ["Sản phẩm", Package],
  ["Nhà cung cấp", Building2],
  ["Đại lý", Store],
  ["Nhập kho", ArrowDownToLine],
  ["Xuất kho", ArrowUpRight],
  ["Tồn kho", Warehouse],
  ["Vị trí kho", MapPin],
  ["Đơn hàng", ShoppingBag],
  ["Điều phối GPS", LocateFixed],
  ["Báo cáo", BarChart3],
  ["Nhân sự", Users],
  ["Cài đặt", Settings],
];

function AdminSidebar({
  page,
  setPage,
  open,
  close,
}: {
  page: string;
  setPage: (p: string) => void;
  open: boolean;
  close: () => void;
}) {
  return (
    <>
      {open && (
        <button
          aria-label="Đóng menu"
          onClick={close}
          className="fixed inset-0 z-30 bg-slate-950/35 lg:hidden"
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-[248px] flex-col border-r border-blue-100 bg-gradient-to-b from-white via-white to-blue-50/70 transition-transform lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="flex h-18 items-center border-b border-slate-100 px-5">
          <Logo />
        </div>
        <nav className="scrollbar-hidden flex-1 overflow-y-auto px-3 py-4">
          <p className="mb-2 px-3 text-[10px] font-bold uppercase tracking-[.14em] text-slate-400">
            Không gian quản trị
          </p>
          {adminNav.map(([label, Icon], index) => (
            <button
              key={label}
              onClick={() => {
                setPage(label);
                close();
              }}
              className={`nav-item ${page === label ? "active" : ""} ${index === 9 ? "mt-3 border-t border-slate-100 pt-4" : ""}`}
            >
              <Icon size={17} strokeWidth={1.9} />
              <span>{label}</span>
              {label === "Đơn hàng" && (
                <span className="ml-auto rounded-md bg-blue-50 px-1.5 py-0.5 text-[10px] font-bold text-blue-600">
                  5
                </span>
              )}
            </button>
          ))}
        </nav>
        <div className="m-3 rounded-xl bg-slate-50 p-3.5">
          <div className="flex items-center gap-2.5">
            <div className="grid size-9 place-items-center rounded-lg bg-blue-100 text-xs font-bold text-blue-700">
              QT
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-slate-800">Quang Trần</p>
              <p className="text-[10px] text-slate-400">Quản trị hệ thống</p>
            </div>
            <MoreHorizontal size={16} className="text-slate-400" />
          </div>
        </div>
      </aside>
    </>
  );
}

function AdminHeader({
  page,
  openMenu,
  notify,
}: {
  page: string;
  openMenu: () => void;
  notify: (s: string) => void;
}) {
  const [quickSearch, setQuickSearch] = useState("");
  return (
    <header className="sticky top-0 z-20 flex h-18 items-center justify-between border-b border-blue-100 bg-white/80 px-4 shadow-[0_4px_24px_rgba(37,99,235,0.04)] backdrop-blur-xl sm:px-7">
      <div className="flex items-center gap-3">
        <button onClick={openMenu} className="icon-button lg:hidden">
          <Menu size={19} />
        </button>
        <div>
          <p className="text-[11px] text-slate-400">
            DistriFlow <span className="px-1">/</span> {page}
          </p>
          <h1 className="mt-0.5 text-lg font-bold tracking-tight text-slate-900">{page}</h1>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
          <input
            value={quickSearch}
            onChange={(event) => setQuickSearch(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && quickSearch.trim()) {
                notify(`Đang tìm kiếm toàn hệ thống: “${quickSearch}”`);
              }
            }}
            className="h-9 w-56 rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 text-xs outline-none transition focus:border-blue-400 focus:bg-white focus:ring-3 focus:ring-blue-100"
            placeholder="Tìm kiếm nhanh..."
          />
        </div>
        <button
          onClick={() => notify("Bạn có 5 cảnh báo vận hành cần xem")}
          className="icon-button relative"
        >
          <Bell size={18} />
          <span className="absolute right-2 top-2 size-1.5 rounded-full bg-red-500 ring-2 ring-white" />
        </button>
        <div className="ml-1 hidden items-center gap-2 border-l border-slate-200 pl-3 sm:flex">
          <div className="grid size-8 place-items-center rounded-full bg-slate-900 text-[10px] font-bold text-white">
            QT
          </div>
          <ChevronDown size={14} className="text-slate-400" />
        </div>
      </div>
    </header>
  );
}

function KpiCard({
  label,
  value,
  change,
  icon: Icon,
  tone,
}: {
  label: string;
  value: string;
  change: string;
  icon: LucideIcon;
  tone: "blue" | "emerald" | "violet" | "amber";
}) {
  const tones = {
    blue: {
      icon: "bg-blue-100 text-blue-600 ring-blue-200",
      card: "from-blue-50/90 to-white border-blue-100",
      bar: "bg-blue-600",
    },
    emerald: {
      icon: "bg-emerald-100 text-emerald-600 ring-emerald-200",
      card: "from-emerald-50/90 to-white border-emerald-100",
      bar: "bg-emerald-500",
    },
    violet: {
      icon: "bg-violet-100 text-violet-600 ring-violet-200",
      card: "from-violet-50/90 to-white border-violet-100",
      bar: "bg-violet-500",
    },
    amber: {
      icon: "bg-amber-100 text-amber-600 ring-amber-200",
      card: "from-amber-50/90 to-white border-amber-100",
      bar: "bg-amber-500",
    },
  };
  return (
    <div
      className={`group rounded-xl border bg-gradient-to-br p-4 shadow-[0_8px_28px_rgba(15,23,42,0.05)] transition hover:-translate-y-0.5 hover:shadow-lg ${tones[tone].card} sm:p-5`}
    >
      <div className="flex items-start justify-between">
        <div className={`grid size-10 place-items-center rounded-xl ring-1 ${tones[tone].icon}`}>
          <Icon size={19} />
        </div>
        <span className="flex items-center gap-0.5 rounded-full bg-emerald-50 px-2 py-1 text-[10px] font-bold text-emerald-600">
          <ArrowUpRight size={11} />
          {change}
        </span>
      </div>
      <p className="mt-5 text-[11px] font-semibold uppercase tracking-[.06em] text-slate-400">
        {label}
      </p>
      <p className="mt-1 text-[25px] font-bold tracking-[-.04em] text-slate-900">{value}</p>
      <div className="mt-4 h-1 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full w-2/3 rounded-full ${tones[tone].bar}`} />
      </div>
    </div>
  );
}

function OrdersTable({
  orders,
  onApprove,
  onDelete,
  onEdit,
  onView,
  compact = false,
}: {
  orders: Order[];
  onApprove?: (id: string) => void;
  onDelete?: (id: string) => void;
  onEdit?: (order: Order) => void;
  onView?: (order: Order) => void;
  compact?: boolean;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="data-table min-w-[760px]">
        <thead>
          <tr>
            <th>Mã đơn</th>
            <th>Đại lý</th>
            <th>Ngày tạo</th>
            <th>Sản phẩm</th>
            <th>Tổng tiền</th>
            <th>Trạng thái</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {orders.slice(0, compact ? 4 : orders.length).map((order) => (
            <tr key={order.id}>
              <td>
                {onView ? (
                  <button
                    onClick={() => onView(order)}
                    className="font-bold text-blue-600 hover:underline"
                  >
                    {order.id}
                  </button>
                ) : (
                  <span className="font-bold text-blue-600">{order.id}</span>
                )}
              </td>
              <td>
                <div className="flex items-center gap-2.5">
                  <span className="grid size-8 place-items-center rounded-lg bg-slate-100 text-[10px] font-bold text-slate-600">
                    {order.dealer.slice(0, 2).toUpperCase()}
                  </span>
                  <span className="font-semibold text-slate-700">{order.dealer}</span>
                </div>
              </td>
              <td>{order.date}</td>
              <td>{order.items} mặt hàng</td>
              <td className="font-semibold text-slate-800">{formatMoney(order.total)}</td>
              <td>
                <Status value={order.status} />
              </td>
              <td>
                <div className="flex justify-end gap-1">
                  {order.status === "Chờ duyệt" && onApprove && (
                    <button
                      title="Duyệt đơn"
                      onClick={() => onApprove(order.id)}
                      className="grid size-8 place-items-center rounded-lg text-emerald-600 hover:bg-emerald-50"
                    >
                      <CheckCircle2 size={17} />
                    </button>
                  )}
                  {onDelete && (
                    <button
                      title="Xóa đơn"
                      onClick={() => onDelete(order.id)}
                      className="grid size-8 place-items-center rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-600"
                    >
                      <XCircle size={17} />
                    </button>
                  )}
                  {onEdit && (
                    <button
                      title="Chỉnh sửa"
                      onClick={() => onEdit(order)}
                      className="grid size-8 place-items-center rounded-lg text-slate-400 hover:bg-slate-100"
                    >
                      <MoreHorizontal size={17} />
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AdminDashboard({
  orders,
  onApprove,
  setPage,
  notify,
}: {
  orders: Order[];
  onApprove: (id: string) => void;
  setPage: (p: string) => void;
  notify: (s: string) => void;
}) {
  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm text-slate-500">Chào buổi sáng, Quang!</p>
          <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
            Tình hình vận hành hôm nay
          </h2>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => notify("Dữ liệu Dashboard đang hiển thị 30 ngày gần nhất")}
            className="secondary-button"
          >
            <Filter size={15} />
            30 ngày qua
          </button>
          <button onClick={() => setPage("Đơn hàng")} className="primary-button">
            <Plus size={16} />
            Tạo đơn xuất
          </button>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
        <KpiCard
          label="Giá trị tồn kho"
          value="₫4,82 tỷ"
          change="8,4%"
          icon={CircleDollarSign}
          tone="blue"
        />
        <KpiCard
          label="Đơn hàng tháng này"
          value="1.248"
          change="12,2%"
          icon={ShoppingBag}
          tone="violet"
        />
        <KpiCard
          label="Tỷ lệ giao đúng hẹn"
          value="96,8%"
          change="2,1%"
          icon={Truck}
          tone="emerald"
        />
        <KpiCard
          label="Sản phẩm sắp hết"
          value="24"
          change="3 mới"
          icon={AlertTriangle}
          tone="amber"
        />
      </div>
      <div className="grid gap-5 xl:grid-cols-[1.65fr_1fr]">
        <section className="panel p-4 sm:p-5">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h3 className="section-title">Luồng nhập & xuất kho</h3>
              <p className="section-subtitle">Số kiện hàng trong 30 ngày gần nhất</p>
            </div>
            <button onClick={() => notify("Đã làm mới dữ liệu biểu đồ")} className="icon-button">
              <MoreHorizontal size={18} />
            </button>
          </div>
          <div className="mb-3 flex gap-4 text-[11px] font-medium text-slate-500">
            <span className="flex items-center gap-1.5">
              <i className="size-2 rounded-full bg-blue-600" />
              Nhập kho
            </span>
            <span className="flex items-center gap-1.5">
              <i className="size-2 rounded-full bg-emerald-500" />
              Xuất kho
            </span>
          </div>
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ left: -22, right: 8, top: 10 }}>
                <defs>
                  <linearGradient id="blueArea" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2563EB" stopOpacity={0.18} />
                    <stop offset="100%" stopColor="#2563EB" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#E2E8F0" strokeDasharray="4 4" vertical={false} />
                <XAxis
                  dataKey="day"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#94A3B8", fontSize: 10 }}
                  dy={8}
                />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: "#94A3B8", fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    border: "1px solid #E2E8F0",
                    borderRadius: 10,
                    fontSize: 12,
                    boxShadow: "0 12px 30px rgba(15,23,42,.1)",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="nhap"
                  stroke="#2563EB"
                  strokeWidth={2.5}
                  fill="url(#blueArea)"
                />
                <Area
                  type="monotone"
                  dataKey="xuat"
                  stroke="#10B981"
                  strokeWidth={2.5}
                  fill="transparent"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>
        <section className="panel p-4 sm:p-5">
          <div>
            <h3 className="section-title">Phân bổ tồn kho</h3>
            <p className="section-subtitle">Theo nhóm sản phẩm</p>
          </div>
          <div className="relative mt-2 h-[190px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { n: "Đồ uống", v: 42 },
                    { n: "Thực phẩm", v: 28 },
                    { n: "Gia dụng", v: 18 },
                    { n: "Khác", v: 12 },
                  ]}
                  dataKey="v"
                  innerRadius={60}
                  outerRadius={82}
                  paddingAngle={3}
                  stroke="none"
                >
                  {["#2563EB", "#10B981", "#8B5CF6", "#F59E0B"].map((c) => (
                    <Cell key={c} fill={c} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="pointer-events-none absolute inset-0 grid place-items-center text-center">
              <div>
                <p className="text-2xl font-bold text-slate-900">8.420</p>
                <p className="text-[10px] text-slate-400">SKU đang lưu</p>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[
              ["Đồ uống", "42%", "#2563EB"],
              ["Thực phẩm", "28%", "#10B981"],
              ["Gia dụng", "18%", "#8B5CF6"],
              ["Khác", "12%", "#F59E0B"],
            ].map(([n, v, c]) => (
              <div key={n} className="flex items-center gap-2 text-xs">
                <i className="size-2 rounded-full" style={{ background: c }} />
                <span className="flex-1 text-slate-500">{n}</span>
                <b className="text-slate-800">{v}</b>
              </div>
            ))}
          </div>
        </section>
      </div>
      <div className="grid gap-5 xl:grid-cols-[1.7fr_1fr]">
        <section className="panel overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
            <div>
              <h3 className="section-title">Đơn hàng gần đây</h3>
              <p className="section-subtitle">Cập nhật theo thời gian thực</p>
            </div>
            <button onClick={() => setPage("Đơn hàng")} className="text-button">
              Xem tất cả <ArrowRight size={14} />
            </button>
          </div>
          <OrdersTable orders={orders} onApprove={onApprove} compact />
        </section>
        <section className="panel p-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="section-title">Cảnh báo kho</h3>
              <p className="section-subtitle">Cần xử lý sớm</p>
            </div>
            <span className="rounded-full bg-red-50 px-2 py-1 text-[10px] font-bold text-red-600">
              5 cảnh báo
            </span>
          </div>
          <div className="mt-4 space-y-2.5">
            {[
              [
                "Bánh quy Cosy Marie",
                "Chỉ còn 24 thùng",
                AlertTriangle,
                "text-amber-600 bg-amber-50",
              ],
              ["Kho lạnh B2", "Nhiệt độ tăng 2.4°C", Activity, "text-red-600 bg-red-50"],
              ["Lô NK-09214", "Sắp hết hạn trong 15 ngày", Clock3, "text-violet-600 bg-violet-50"],
            ].map(([a, b, I, c]) => (
              <button
                key={a as string}
                onClick={() => notify(`Đang mở cảnh báo: ${a as string}`)}
                className="flex w-full items-center gap-3 rounded-xl border border-slate-100 p-3 text-left transition hover:border-slate-200 hover:bg-slate-50"
              >
                <span className={`grid size-9 shrink-0 place-items-center rounded-lg ${c}`}>
                  <I size={17} />
                </span>
                <span className="min-w-0 flex-1">
                  <b className="block truncate text-xs text-slate-800">{a as string}</b>
                  <small className="text-[10px] text-slate-400">{b as string}</small>
                </span>
                <ChevronRight size={14} className="text-slate-300" />
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

function AdminOrders({
  orders,
  onApprove,
  onDelete,
  onSave,
}: {
  orders: Order[];
  onApprove: (id: string) => void;
  onDelete: (id: string) => void;
  onSave: (order: Order) => void;
}) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"Tất cả" | OrderStatus>("Tất cả");
  const [editing, setEditing] = useState<Order | "new" | null>(null);
  const [viewing, setViewing] = useState<Order | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 4;
  const shown = orders.filter(
    (o) =>
      (o.dealer.toLowerCase().includes(query.toLowerCase()) ||
        o.id.toLowerCase().includes(query.toLowerCase())) &&
      (filter === "Tất cả" || o.status === filter),
  );
  const totalPages = Math.max(1, Math.ceil(shown.length / pageSize));
  const pagedOrders = shown.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm text-slate-500">Quản lý toàn bộ vòng đời đơn hàng</p>
          <h2 className="mt-1 text-2xl font-bold text-slate-900">Đơn hàng phân phối</h2>
        </div>
        <button onClick={() => setEditing("new")} className="primary-button">
          <Plus size={16} />
          Tạo đơn hàng
        </button>
      </div>
      <div className="panel overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-slate-100 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative flex-1 sm:max-w-xs">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="input pl-9"
              placeholder="Tìm mã đơn, đại lý..."
            />
          </div>
          <div className="flex gap-2 overflow-x-auto">
            {(["Tất cả", "Chờ duyệt", "Đã duyệt", "Đang giao", "Hoàn thành"] as const).map((s) => (
              <button
                key={s}
                onClick={() => {
                  setFilter(s);
                  setCurrentPage(1);
                }}
                className={`whitespace-nowrap rounded-lg px-3 py-2 text-xs font-semibold ${filter === s ? "bg-slate-900 text-white" : "bg-slate-50 text-slate-500 hover:bg-slate-100"}`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
        {shown.length ? (
          <OrdersTable
            orders={pagedOrders}
            onApprove={onApprove}
            onDelete={onDelete}
            onEdit={setEditing}
            onView={setViewing}
          />
        ) : (
          <div className="grid h-52 place-items-center text-center">
            <div>
              <PackageOpen className="mx-auto text-slate-300" size={36} />
              <p className="mt-2 text-sm font-semibold text-slate-600">Không tìm thấy đơn hàng</p>
            </div>
          </div>
        )}
        <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-xs text-slate-400">
          <span>
            Hiển thị {shown.length} / {orders.length} đơn hàng
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
              disabled={currentPage === 1}
              className="icon-button size-8 disabled:opacity-30"
            >
              <ChevronLeft size={14} />
            </button>
            <button className="grid size-8 place-items-center rounded-lg bg-blue-600 text-white">
              {currentPage}
            </button>
            <button
              onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
              disabled={currentPage === totalPages}
              className="icon-button size-8 disabled:opacity-30"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>
      {editing && (
        <OrderModal
          order={editing === "new" ? undefined : editing}
          onClose={() => setEditing(null)}
          onSave={(order) => {
            onSave(order);
            setEditing(null);
          }}
        />
      )}
      {viewing && (
        <DetailModal
          title={`Chi tiết đơn ${viewing.id}`}
          subtitle={viewing.dealer}
          onClose={() => setViewing(null)}
          rows={[
            ["Trạng thái", viewing.status],
            ["Ngày tạo", viewing.date],
            ["Số mặt hàng", `${viewing.items} mặt hàng`],
            ["Tổng giá trị", formatMoney(viewing.total)],
            ["Địa chỉ giao", viewing.address],
          ]}
        />
      )}
    </div>
  );
}

function OrderModal({
  order,
  onClose,
  onSave,
}: {
  order?: Order;
  onClose: () => void;
  onSave: (order: Order) => void;
}) {
  const [dealer, setDealer] = useState(order?.dealer || "");
  const [address, setAddress] = useState(order?.address || "");
  const [items, setItems] = useState(order?.items || 1);
  const [total, setTotal] = useState(order?.total || 0);
  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!dealer.trim() || !address.trim() || total <= 0) return;
    onSave({
      id: order?.id || `DH-${String(Date.now()).slice(-6)}`,
      dealer,
      address,
      items,
      total,
      date: order?.date || "29/06/2025",
      status: order?.status || "Chờ duyệt",
    });
  };
  return (
    <div className="fixed inset-0 z-[90] grid place-items-center bg-slate-950/45 p-4 backdrop-blur-sm">
      <button aria-label="Đóng" onClick={onClose} className="absolute inset-0" />
      <form onSubmit={submit} className="relative w-full max-w-lg rounded-2xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              {order ? "Chỉnh sửa đơn hàng" : "Tạo đơn hàng mới"}
            </h3>
            <p className="mt-0.5 text-[10px] text-slate-400">Thông tin phân phối và giao nhận</p>
          </div>
          <button type="button" onClick={onClose} className="icon-button">
            <X size={18} />
          </button>
        </div>
        <div className="grid gap-4 p-5 sm:grid-cols-2">
          <label className="sm:col-span-2">
            <span className="field-label">Tên đại lý</span>
            <input
              value={dealer}
              onChange={(e) => setDealer(e.target.value)}
              className="input mt-1.5"
              placeholder="Nhập tên đại lý"
              autoFocus
            />
          </label>
          <label>
            <span className="field-label">Số mặt hàng</span>
            <input
              type="number"
              min="1"
              value={items}
              onChange={(e) => setItems(Number(e.target.value))}
              className="input mt-1.5"
            />
          </label>
          <label>
            <span className="field-label">Tổng giá trị (VND)</span>
            <input
              type="number"
              min="1"
              value={total}
              onChange={(e) => setTotal(Number(e.target.value))}
              className="input mt-1.5"
              placeholder="12000000"
            />
          </label>
          <label className="sm:col-span-2">
            <span className="field-label">Địa chỉ giao hàng</span>
            <input
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="input mt-1.5"
              placeholder="Số nhà, đường, quận/huyện, tỉnh thành"
            />
          </label>
        </div>
        <div className="flex justify-end gap-2 border-t border-slate-100 px-5 py-4">
          <button type="button" onClick={onClose} className="secondary-button">
            Hủy bỏ
          </button>
          <button type="submit" className="primary-button">
            <Check size={15} />
            {order ? "Lưu thay đổi" : "Tạo đơn hàng"}
          </button>
        </div>
      </form>
    </div>
  );
}

type AdminRecord = {
  id: string;
  name: string;
  meta: string;
  value: string;
  status: string;
};

const adminRecords: Record<string, AdminRecord[]> = {
  "Sản phẩm": products.map((p) => ({
    id: p.sku,
    name: p.name,
    meta: p.category,
    value: `${p.stock.toLocaleString("vi-VN")} thùng`,
    status: p.stock < 50 ? "Sắp hết" : "Đang kinh doanh",
  })),
  "Nhà cung cấp": [
    {
      id: "NCC-001",
      name: "Công ty Lavie Việt Nam",
      meta: "Đồ uống",
      value: "18 hợp đồng",
      status: "Đang hợp tác",
    },
    {
      id: "NCC-002",
      name: "TH True Milk",
      meta: "Sữa & dinh dưỡng",
      value: "12 hợp đồng",
      status: "Đang hợp tác",
    },
    {
      id: "NCC-003",
      name: "Acecook Việt Nam",
      meta: "Thực phẩm",
      value: "8 hợp đồng",
      status: "Chờ duyệt",
    },
    {
      id: "NCC-004",
      name: "Unilever Việt Nam",
      meta: "Hàng gia dụng",
      value: "24 hợp đồng",
      status: "Đang hợp tác",
    },
  ],
  "Đại lý": [
    {
      id: "DL-1024",
      name: "Đại lý Minh Phát",
      meta: "TP. Hồ Chí Minh",
      value: "₫186 triệu",
      status: "Hoạt động",
    },
    {
      id: "DL-0982",
      name: "Siêu thị An Nhiên",
      meta: "TP. Thủ Đức",
      value: "₫142 triệu",
      status: "Hoạt động",
    },
    {
      id: "DL-0864",
      name: "Tạp hóa Thành Công",
      meta: "Gò Vấp",
      value: "₫96 triệu",
      status: "Cần xác minh",
    },
    {
      id: "DL-0751",
      name: "Mart 365 Bình Thạnh",
      meta: "Bình Thạnh",
      value: "₫214 triệu",
      status: "Hoạt động",
    },
  ],
  "Nhập kho": [
    {
      id: "NK-250629",
      name: "Nhập hàng Lavie tháng 6",
      meta: "Kho trung tâm A",
      value: "1.200 thùng",
      status: "Đang xử lý",
    },
    {
      id: "NK-250627",
      name: "Nhập sữa TH True Milk",
      meta: "Kho lạnh B2",
      value: "480 thùng",
      status: "Hoàn thành",
    },
    {
      id: "NK-250625",
      name: "Nhập hàng Unilever",
      meta: "Kho trung tâm A",
      value: "820 thùng",
      status: "Hoàn thành",
    },
  ],
  "Xuất kho": [
    {
      id: "XK-250629",
      name: "Xuất cho Đại lý Minh Phát",
      meta: "Kho trung tâm A",
      value: "68 kiện",
      status: "Chờ xuất kho",
    },
    {
      id: "XK-250628",
      name: "Xuất cho Siêu thị An Nhiên",
      meta: "Kho trung tâm A",
      value: "112 kiện",
      status: "Đã bàn giao",
    },
    {
      id: "XK-250627",
      name: "Xuất cho Mart 365",
      meta: "Kho lạnh B2",
      value: "46 kiện",
      status: "Đã bàn giao",
    },
  ],
  "Tồn kho": products.map((p) => ({
    id: p.sku,
    name: p.name,
    meta: p.stock < 100 ? "Khu C • Tầng 1" : "Khu A • Tầng 2",
    value: `${p.stock.toLocaleString("vi-VN")} thùng`,
    status: p.stock < 50 ? "Cần nhập thêm" : "Đủ tồn",
  })),
  "Vị trí kho": [
    {
      id: "KHO-A01",
      name: "Kho trung tâm A",
      meta: "Quận 7, TP.HCM",
      value: "82% công suất",
      status: "Đang vận hành",
    },
    {
      id: "KHO-B02",
      name: "Kho lạnh B2",
      meta: "TP. Thủ Đức",
      value: "64% công suất",
      status: "Đang vận hành",
    },
    {
      id: "KHO-C03",
      name: "Kho trung chuyển C",
      meta: "Bình Chánh",
      value: "38% công suất",
      status: "Bảo trì",
    },
  ],
  "Điều phối GPS": [
    {
      id: "59C1-123.45",
      name: "Nguyễn Minh",
      meta: "Tuyến Quận 7 → Thủ Đức",
      value: "4/7 điểm",
      status: "Đang giao",
    },
    {
      id: "51D-882.16",
      name: "Trần Quốc Anh",
      meta: "Tuyến Gò Vấp → Quận 12",
      value: "6/8 điểm",
      status: "Đang giao",
    },
    {
      id: "50H-221.09",
      name: "Lê Thanh Tùng",
      meta: "Tuyến Bình Thạnh → Quận 1",
      value: "5/5 điểm",
      status: "Hoàn thành",
    },
  ],
  "Báo cáo": [
    {
      id: "BC-0625-01",
      name: "Báo cáo doanh thu tháng 6",
      meta: "Tài chính",
      value: "Cập nhật 29/06",
      status: "Sẵn sàng",
    },
    {
      id: "BC-0625-02",
      name: "Hiệu suất giao hàng",
      meta: "Vận hành",
      value: "Cập nhật 29/06",
      status: "Sẵn sàng",
    },
    {
      id: "BC-0625-03",
      name: "Tuổi tồn kho theo SKU",
      meta: "Kho vận",
      value: "Cập nhật 28/06",
      status: "Đang tạo",
    },
  ],
  "Nhân sự": [
    {
      id: "NV-0018",
      name: "Quang Trần",
      meta: "Quản trị hệ thống",
      value: "Khối vận hành",
      status: "Đang làm việc",
    },
    {
      id: "NV-0042",
      name: "Nguyễn Minh",
      meta: "Tài xế giao hàng",
      value: "Đội giao nhận 01",
      status: "Đang làm việc",
    },
    {
      id: "NV-0037",
      name: "Hoàng Anh",
      meta: "Quản lý kho",
      value: "Kho trung tâm A",
      status: "Đang làm việc",
    },
  ],
  "Cài đặt": [
    {
      id: "SET-01",
      name: "Thông tin doanh nghiệp",
      meta: "Hồ sơ & nhận diện",
      value: "Đã cập nhật",
      status: "Hoàn tất",
    },
    {
      id: "SET-02",
      name: "Quy trình phê duyệt",
      meta: "Đơn hàng & nhập xuất",
      value: "2 cấp duyệt",
      status: "Đang áp dụng",
    },
    {
      id: "SET-03",
      name: "Thông báo hệ thống",
      meta: "Email & ứng dụng",
      value: "8 quy tắc",
      status: "Đang áp dụng",
    },
  ],
};

function GenericAdminPage({ page, notify }: { page: string; notify: (s: string) => void }) {
  const [rows, setRows] = useState(adminRecords[page] || adminRecords["Sản phẩm"]);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("Tất cả");
  const [editing, setEditing] = useState<AdminRecord | "new" | null>(null);
  const [viewing, setViewing] = useState<AdminRecord | null>(null);
  const statuses = ["Tất cả", ...Array.from(new Set(rows.map((row) => row.status)))];
  const shown = rows.filter(
    (row) =>
      `${row.id} ${row.name} ${row.meta}`.toLowerCase().includes(query.toLowerCase()) &&
      (statusFilter === "Tất cả" || row.status === statusFilter),
  );
  const saveRecord = (record: AdminRecord) => {
    setRows((current) =>
      current.some((row) => row.id === record.id)
        ? current.map((row) => (row.id === record.id ? record : row))
        : [record, ...current],
    );
    setEditing(null);
    notify(`Đã lưu ${record.name}`);
  };
  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm text-slate-500">Danh mục và dữ liệu vận hành</p>
          <h2 className="mt-1 text-2xl font-bold text-slate-900">{page}</h2>
        </div>
        <button onClick={() => setEditing("new")} className="primary-button">
          <Plus size={16} />
          Thêm mới
        </button>
      </div>
      <div className="panel overflow-hidden">
        <div className="flex gap-2 border-b border-slate-100 p-4">
          <div className="relative max-w-sm flex-1">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="input pl-9"
              placeholder={`Tìm kiếm ${page.toLowerCase()}...`}
            />
          </div>
          <div className="relative">
            <Filter
              size={15}
              className="pointer-events-none absolute left-3 top-1/2 z-10 -translate-y-1/2 text-slate-400"
            />
            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
              className="secondary-button appearance-none pl-9 pr-8"
            >
              {statuses.map((status) => (
                <option key={status}>{status}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="data-table min-w-[680px]">
            <thead>
              <tr>
                <th>Mã tham chiếu</th>
                <th>Tên / Nội dung</th>
                <th>Phân loại</th>
                <th>Giá trị</th>
                <th>Trạng thái</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {shown.map((record) => (
                <tr key={record.id}>
                  <td className="font-mono text-[11px] text-blue-600">{record.id}</td>
                  <td>
                    <div className="flex items-center gap-3">
                      <span className="grid size-9 rounded-lg bg-blue-50 place-items-center text-blue-600">
                        <Package size={16} />
                      </span>
                      <button
                        onClick={() => setViewing(record)}
                        className="font-bold text-slate-700 hover:text-blue-600"
                      >
                        {record.name}
                      </button>
                    </div>
                  </td>
                  <td>{record.meta}</td>
                  <td className="font-semibold">{record.value}</td>
                  <td>
                    <span
                      className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${/chờ|cần|bảo trì|đang tạo/i.test(record.status) ? "bg-amber-50 text-amber-700" : "bg-emerald-50 text-emerald-700"}`}
                    >
                      {record.status}
                    </span>
                  </td>
                  <td>
                    <div className="flex justify-end gap-1">
                      <button
                        title="Chỉnh sửa"
                        onClick={() => setEditing(record)}
                        className="icon-button size-8"
                      >
                        <MoreHorizontal size={16} />
                      </button>
                      <button
                        title="Xóa"
                        onClick={() => {
                          setRows((current) => current.filter((row) => row.id !== record.id));
                          notify(`Đã xóa ${record.name}`);
                        }}
                        className="icon-button size-8 hover:text-red-600"
                      >
                        <X size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!shown.length && (
          <div className="grid h-40 place-items-center text-sm text-slate-400">
            Không tìm thấy dữ liệu phù hợp
          </div>
        )}
        <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-[11px] text-slate-400">
          <span>Hiển thị {shown.length} bản ghi</span>
          <button onClick={() => notify(`Đã xuất dữ liệu ${page}`)} className="text-button">
            Xuất dữ liệu <ArrowUpRight size={13} />
          </button>
        </div>
      </div>
      {editing && (
        <RecordModal
          page={page}
          record={editing === "new" ? undefined : editing}
          onClose={() => setEditing(null)}
          onSave={saveRecord}
        />
      )}
      {viewing && (
        <DetailModal
          title={viewing.name}
          subtitle={viewing.id}
          onClose={() => setViewing(null)}
          rows={[
            ["Phân loại", viewing.meta],
            ["Giá trị", viewing.value],
            ["Trạng thái", viewing.status],
          ]}
        />
      )}
    </div>
  );
}

function RecordModal({
  page,
  record,
  onClose,
  onSave,
}: {
  page: string;
  record?: AdminRecord;
  onClose: () => void;
  onSave: (record: AdminRecord) => void;
}) {
  const [name, setName] = useState(record?.name || "");
  const [meta, setMeta] = useState(record?.meta || "");
  const [value, setValue] = useState(record?.value || "");
  const [status, setStatus] = useState(record?.status || "Đang hoạt động");
  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!name.trim() || !meta.trim()) return;
    onSave({
      id: record?.id || `${page.slice(0, 2).toUpperCase()}-${String(Date.now()).slice(-4)}`,
      name,
      meta,
      value: value || "Chưa cập nhật",
      status,
    });
  };
  return (
    <div className="fixed inset-0 z-[90] grid place-items-center bg-slate-950/45 p-4 backdrop-blur-sm">
      <button aria-label="Đóng" onClick={onClose} className="absolute inset-0" />
      <form onSubmit={submit} className="relative w-full max-w-lg rounded-2xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              {record ? `Chỉnh sửa ${page.toLowerCase()}` : `Thêm ${page.toLowerCase()}`}
            </h3>
            <p className="mt-0.5 text-[10px] text-slate-400">
              Mọi thay đổi được cập nhật vào mock data
            </p>
          </div>
          <button type="button" onClick={onClose} className="icon-button">
            <X size={18} />
          </button>
        </div>
        <div className="grid gap-4 p-5 sm:grid-cols-2">
          <label className="sm:col-span-2">
            <span className="field-label">Tên / nội dung</span>
            <input
              autoFocus
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="input mt-1.5"
              placeholder={`Nhập tên ${page.toLowerCase()}`}
            />
          </label>
          <label>
            <span className="field-label">Phân loại</span>
            <input
              value={meta}
              onChange={(event) => setMeta(event.target.value)}
              className="input mt-1.5"
              placeholder="Nhóm hoặc vị trí"
            />
          </label>
          <label>
            <span className="field-label">Giá trị</span>
            <input
              value={value}
              onChange={(event) => setValue(event.target.value)}
              className="input mt-1.5"
              placeholder="Số lượng hoặc giá trị"
            />
          </label>
          <label className="sm:col-span-2">
            <span className="field-label">Trạng thái</span>
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              className="input mt-1.5"
            >
              <option>Đang hoạt động</option>
              <option>Chờ duyệt</option>
              <option>Hoàn thành</option>
              <option>Tạm dừng</option>
            </select>
          </label>
        </div>
        <div className="flex justify-end gap-2 border-t border-slate-100 px-5 py-4">
          <button type="button" onClick={onClose} className="secondary-button">
            Hủy bỏ
          </button>
          <button type="submit" className="primary-button">
            <Check size={15} />
            Lưu dữ liệu
          </button>
        </div>
      </form>
    </div>
  );
}

function DetailModal({
  title,
  subtitle,
  rows,
  onClose,
}: {
  title: string;
  subtitle: string;
  rows: [string, string][];
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-[95] grid place-items-center bg-slate-950/45 p-4 backdrop-blur-sm">
      <button aria-label="Đóng" onClick={onClose} className="absolute inset-0" />
      <div className="relative w-full max-w-md rounded-2xl bg-white p-5 shadow-2xl">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-blue-600">
              {subtitle}
            </p>
            <h3 className="mt-1 text-lg font-bold text-slate-900">{title}</h3>
          </div>
          <button onClick={onClose} className="icon-button">
            <X size={18} />
          </button>
        </div>
        <div className="mt-5 divide-y divide-slate-100 rounded-xl border border-slate-100">
          {rows.map(([label, value]) => (
            <div key={label} className="flex items-start justify-between gap-5 px-4 py-3 text-xs">
              <span className="text-slate-400">{label}</span>
              <b className="text-right text-slate-700">{value}</b>
            </div>
          ))}
        </div>
        <button onClick={onClose} className="primary-button mt-5 w-full">
          Đóng chi tiết
        </button>
      </div>
    </div>
  );
}

function AdminApp({
  orders,
  setOrders,
  notify,
}: {
  orders: Order[];
  setOrders: React.Dispatch<React.SetStateAction<Order[]>>;
  notify: (s: string) => void;
}) {
  const [page, setPage] = useState("Tổng quan");
  const [menu, setMenu] = useState(false);
  const approve = (id: string) => {
    setOrders((prev) => prev.map((o) => (o.id === id ? { ...o, status: "Đã duyệt" } : o)));
    notify(`Đã duyệt đơn ${id} và chuyển sang xuất kho`);
  };
  const remove = (id: string) => {
    setOrders((prev) => prev.filter((o) => o.id !== id));
    notify(`Đã xóa đơn ${id}`);
  };
  const save = (order: Order) => {
    setOrders((prev) =>
      prev.some((item) => item.id === order.id)
        ? prev.map((item) => (item.id === order.id ? order : item))
        : [order, ...prev],
    );
    notify(`Đã lưu đơn hàng ${order.id}`);
  };
  return (
    <div className="admin-shell min-h-screen">
      <AdminSidebar page={page} setPage={setPage} open={menu} close={() => setMenu(false)} />
      <div className="lg:pl-[248px]">
        <AdminHeader page={page} openMenu={() => setMenu(true)} notify={notify} />
        <main className="mx-auto max-w-[1600px] p-4 pb-28 sm:p-7 sm:pb-28">
          {page === "Tổng quan" ? (
            <AdminDashboard orders={orders} onApprove={approve} setPage={setPage} notify={notify} />
          ) : page === "Đơn hàng" ? (
            <AdminOrders orders={orders} onApprove={approve} onDelete={remove} onSave={save} />
          ) : (
            <GenericAdminPage key={page} page={page} notify={notify} />
          )}
        </main>
      </div>
    </div>
  );
}

function PartnerHeader({
  cartCount,
  setPage,
}: {
  cartCount: number;
  setPage: (p: string) => void;
}) {
  return (
    <header className="sticky top-0 z-20 border-b border-emerald-100 bg-white/85 shadow-[0_4px_24px_rgba(5,150,105,0.06)] backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[1440px] items-center justify-between px-4 sm:px-7">
        <Logo />
        <nav className="hidden gap-7 md:flex">
          {["Danh mục", "Đơn hàng", "Theo dõi giao hàng"].map((x) => (
            <button
              key={x}
              onClick={() => setPage(x)}
              className="text-xs font-semibold text-slate-500 hover:text-emerald-600"
            >
              {x}
            </button>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <button onClick={() => setPage("Giỏ hàng")} className="icon-button relative">
            <ShoppingCart size={18} />
            {cartCount > 0 && (
              <span className="absolute -right-1 -top-1 grid size-4 place-items-center rounded-full bg-emerald-600 text-[9px] font-bold text-white">
                {cartCount}
              </span>
            )}
          </button>
          <div className="hidden rounded-lg bg-emerald-50 px-3 py-2 text-[11px] font-bold text-emerald-700 sm:block">
            Đại lý Minh Phát
          </div>
        </div>
      </div>
    </header>
  );
}

function PartnerApp({
  orders,
  setOrders,
  notify,
}: {
  orders: Order[];
  setOrders: React.Dispatch<React.SetStateAction<Order[]>>;
  notify: (s: string) => void;
}) {
  const [page, setPage] = useState("Danh mục");
  const [cart, setCart] = useState<Record<number, number>>({});
  const [query, setQuery] = useState("");
  const count = Object.values(cart).reduce((a, b) => a + b, 0);
  const total = products.reduce((sum, p) => sum + (cart[p.id] || 0) * p.price, 0);
  const placeOrder = () => {
    if (!count) return;
    const id = `DH-${String(Date.now()).slice(-6)}`;
    setOrders((prev) => [
      {
        id,
        dealer: "Đại lý Minh Phát",
        items: count,
        total,
        status: "Chờ duyệt",
        date: "29/06/2025",
        address: "128 Nguyễn Văn Linh, Q.7, TP.HCM",
      },
      ...prev,
    ]);
    setCart({});
    setPage("Đơn hàng");
    notify(`Đặt hàng thành công. Mã đơn ${id}`);
  };
  return (
    <div className="partner-shell min-h-screen pb-28">
      <PartnerHeader cartCount={count} setPage={setPage} />
      <main className="mx-auto max-w-[1440px] px-4 py-6 sm:px-7">
        <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <div className="mb-2 inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-emerald-700">
              <Sparkles size={11} />
              Cổng thông tin đại lý
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Mua hàng sỉ dễ dàng hơn
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Giá tốt, tồn kho trực tiếp và giao hàng minh bạch.
            </p>
          </div>
          <span className="inline-flex w-fit items-center gap-2 rounded-xl border border-emerald-100 bg-emerald-50 px-3 py-2 text-xs font-bold text-emerald-700">
            <CheckCircle2 size={15} /> Công nợ trong hạn
          </span>
        </div>
        {page === "Danh mục" ? (
          <>
            <section className="mb-6 overflow-hidden rounded-2xl bg-slate-950 text-white">
              <div className="relative flex min-h-[180px] items-center px-6 py-8 sm:px-10">
                <img
                  src={productPhotos[1]}
                  alt="Kho hàng DistriFlow"
                  className="absolute inset-0 size-full object-cover opacity-25"
                />
                <div className="relative max-w-xl">
                  <span className="text-xs font-bold uppercase tracking-[.18em] text-emerald-400">
                    Ưu đãi tháng 6
                  </span>
                  <h2 className="mt-2 text-2xl font-bold sm:text-3xl">
                    Tối ưu nguồn hàng, tăng trưởng doanh thu
                  </h2>
                  <p className="mt-2 text-sm text-slate-300">
                    Miễn phí vận chuyển cho đơn hàng từ 10 triệu đồng tại khu vực TP.HCM.
                  </p>
                  <button
                    onClick={() =>
                      notify("Đã áp dụng ưu đãi miễn phí vận chuyển cho đơn từ 10 triệu")
                    }
                    className="mt-5 rounded-lg bg-white px-4 py-2.5 text-xs font-bold text-slate-900"
                  >
                    Xem ưu đãi
                  </button>
                </div>
              </div>
            </section>
            <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Danh mục sản phẩm</h2>
                <p className="text-xs text-slate-400">{products.length} sản phẩm đang sẵn hàng</p>
              </div>
              <div className="relative">
                <Search
                  size={15}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                />
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="input w-full pl-9 sm:w-64"
                  placeholder="Tìm sản phẩm..."
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-4">
              {products
                .filter((p) => p.name.toLowerCase().includes(query.toLowerCase()))
                .map((p) => (
                  <article
                    key={p.id}
                    className="group overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
                  >
                    <div className="relative h-32 overflow-hidden bg-slate-100 sm:h-44">
                      <img
                        src={p.image}
                        alt={p.name}
                        className="size-full object-cover transition duration-500 group-hover:scale-105"
                      />
                      <span className="absolute left-3 top-3 rounded-md bg-white/90 px-2 py-1 text-[9px] font-bold text-slate-600 backdrop-blur">
                        {p.category}
                      </span>
                    </div>
                    <div className="p-3 sm:p-4">
                      <p className="text-[10px] font-medium text-slate-400">{p.sku}</p>
                      <h3 className="mt-1 line-clamp-2 min-h-9 text-xs font-bold text-slate-800 sm:text-sm">
                        {p.name}
                      </h3>
                      <div className="mt-3 flex items-end justify-between">
                        <div>
                          <p className="text-sm font-extrabold text-emerald-700 sm:text-base">
                            {formatMoney(p.price)}
                          </p>
                          <p className="text-[9px] text-slate-400">/ thùng • Còn {p.stock}</p>
                        </div>
                        <button
                          onClick={() => setCart((c) => ({ ...c, [p.id]: (c[p.id] || 0) + 1 }))}
                          className="grid size-9 place-items-center rounded-lg bg-emerald-600 text-white shadow-md shadow-emerald-600/20 hover:bg-emerald-700"
                        >
                          <Plus size={17} />
                        </button>
                      </div>
                    </div>
                  </article>
                ))}
            </div>
          </>
        ) : page === "Giỏ hàng" ? (
          <CartView cart={cart} setCart={setCart} total={total} placeOrder={placeOrder} />
        ) : page === "Theo dõi giao hàng" ? (
          <TrackingView orders={orders} notify={notify} />
        ) : (
          <PartnerOrders orders={orders} />
        )}
      </main>
      <div className="fixed inset-x-0 bottom-0 z-20 border-t border-slate-200 bg-white px-3 pb-[max(10px,env(safe-area-inset-bottom))] pt-2 md:hidden">
        <div className="grid grid-cols-3">
          {[
            ["Danh mục", Store],
            ["Đơn hàng", ShoppingBag],
            ["Giỏ hàng", ShoppingCart],
          ].map(([n, I]) => (
            <button
              key={n as string}
              onClick={() => setPage(n as string)}
              className={`flex flex-col items-center gap-1 py-1 text-[10px] font-semibold ${page === n ? "text-emerald-600" : "text-slate-400"}`}
            >
              <I size={18} />
              {n as string}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function CartView({
  cart,
  setCart,
  total,
  placeOrder,
}: {
  cart: Record<number, number>;
  setCart: React.Dispatch<React.SetStateAction<Record<number, number>>>;
  total: number;
  placeOrder: () => void;
}) {
  const lines = products.filter((p) => cart[p.id]);
  return (
    <div className="mx-auto grid max-w-5xl gap-5 lg:grid-cols-[1.5fr_1fr]">
      <section className="panel overflow-hidden">
        <div className="border-b border-slate-100 p-5">
          <h2 className="text-lg font-bold">Giỏ hàng của bạn</h2>
          <p className="text-xs text-slate-400">{lines.length} sản phẩm đã chọn</p>
        </div>
        {lines.length ? (
          lines.map((p) => (
            <div
              key={p.id}
              className="flex items-center gap-3 border-b border-slate-100 p-4 last:border-0"
            >
              <img src={p.image} className="size-16 rounded-xl object-cover" alt="" />
              <div className="min-w-0 flex-1">
                <b className="block truncate text-sm text-slate-800">{p.name}</b>
                <span className="text-xs font-bold text-emerald-700">{formatMoney(p.price)}</span>
              </div>
              <div className="flex items-center rounded-lg border border-slate-200">
                <button
                  onClick={() => setCart((c) => ({ ...c, [p.id]: Math.max(0, c[p.id] - 1) }))}
                  className="p-2"
                >
                  <Minus size={13} />
                </button>
                <span className="w-7 text-center text-xs font-bold">{cart[p.id]}</span>
                <button
                  onClick={() => setCart((c) => ({ ...c, [p.id]: c[p.id] + 1 }))}
                  className="p-2"
                >
                  <Plus size={13} />
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="grid h-56 place-items-center text-center">
            <div>
              <ShoppingCart className="mx-auto text-slate-300" size={38} />
              <p className="mt-2 text-sm font-semibold text-slate-600">Giỏ hàng đang trống</p>
            </div>
          </div>
        )}
      </section>
      <aside className="panel h-fit p-5">
        <h3 className="font-bold text-slate-900">Tóm tắt đơn hàng</h3>
        <div className="mt-5 space-y-3 text-sm">
          <div className="flex justify-between text-slate-500">
            <span>Tạm tính</span>
            <span>{formatMoney(total)}</span>
          </div>
          <div className="flex justify-between text-slate-500">
            <span>Vận chuyển</span>
            <span className="font-semibold text-emerald-600">Miễn phí</span>
          </div>
          <div className="flex justify-between border-t border-slate-100 pt-4 font-bold">
            <span>Tổng cộng</span>
            <span className="text-lg text-emerald-700">{formatMoney(total)}</span>
          </div>
        </div>
        <button
          disabled={!lines.length}
          onClick={placeOrder}
          className="mt-5 w-full rounded-xl bg-emerald-600 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-600/20 disabled:opacity-40"
        >
          Xác nhận đặt hàng
        </button>
      </aside>
    </div>
  );
}

function PartnerOrders({ orders }: { orders: Order[] }) {
  const [viewing, setViewing] = useState<Order | null>(null);
  return (
    <>
      <div className="panel mx-auto max-w-5xl overflow-hidden">
        <div className="border-b border-slate-100 p-5">
          <h2 className="text-lg font-bold text-slate-900">Đơn hàng của Đại lý Minh Phát</h2>
          <p className="text-xs text-slate-400">Theo dõi phê duyệt và tiến độ giao hàng</p>
        </div>
        <OrdersTable
          orders={orders.filter((o) => o.dealer === "Đại lý Minh Phát")}
          onView={setViewing}
        />
      </div>
      {viewing && (
        <DetailModal
          title={`Đơn hàng ${viewing.id}`}
          subtitle={viewing.status}
          onClose={() => setViewing(null)}
          rows={[
            ["Ngày tạo", viewing.date],
            ["Số lượng", `${viewing.items} mặt hàng`],
            ["Tổng tiền", formatMoney(viewing.total)],
            ["Địa chỉ", viewing.address],
          ]}
        />
      )}
    </>
  );
}

function TrackingView({ orders, notify }: { orders: Order[]; notify: (s: string) => void }) {
  const active = orders.find(
    (order) =>
      order.dealer === "Đại lý Minh Phát" && ["Đã duyệt", "Đang giao"].includes(order.status),
  );
  if (!active) {
    return (
      <div className="panel mx-auto grid min-h-72 max-w-3xl place-items-center text-center">
        <div>
          <Truck size={42} className="mx-auto text-slate-300" />
          <h2 className="mt-3 font-bold text-slate-800">Chưa có chuyến giao đang hoạt động</h2>
          <p className="mt-1 text-xs text-slate-400">Đơn đã duyệt sẽ xuất hiện tại đây.</p>
        </div>
      </div>
    );
  }
  const currentStep = active.status === "Đang giao" ? 3 : 2;
  const steps = ["Đã tiếp nhận", "Đã duyệt", "Đang giao", "Hoàn thành"];
  return (
    <div className="mx-auto grid max-w-5xl gap-5 lg:grid-cols-[1.35fr_1fr]">
      <section className="panel overflow-hidden">
        <div className="border-b border-slate-100 p-5">
          <p className="text-[10px] font-bold text-emerald-600">{active.id}</p>
          <h2 className="mt-1 text-lg font-bold text-slate-900">Theo dõi chuyến giao</h2>
        </div>
        <div className="relative h-64 overflow-hidden bg-[#E8EEE8]">
          <div
            className="absolute inset-0 opacity-60"
            style={{
              backgroundImage:
                "linear-gradient(30deg, transparent 48%, #cbd5e1 49%, #cbd5e1 51%, transparent 52%),linear-gradient(120deg, transparent 48%, #cbd5e1 49%, #cbd5e1 51%, transparent 52%)",
              backgroundSize: "70px 70px",
            }}
          />
          <svg className="absolute inset-0 size-full" viewBox="0 0 600 260">
            <path
              d="M40 210 C140 180,150 60,260 105 S430 210,555 50"
              fill="none"
              stroke="#059669"
              strokeWidth="6"
              strokeLinecap="round"
              strokeDasharray="9 8"
            />
          </svg>
          <span className="absolute bottom-8 left-10 grid size-10 place-items-center rounded-full bg-slate-900 text-white ring-4 ring-white">
            <Store size={18} />
          </span>
          <span className="absolute right-8 top-9 grid size-10 place-items-center rounded-full bg-emerald-600 text-white ring-4 ring-white">
            <Truck size={18} />
          </span>
          <div className="absolute bottom-3 right-3 rounded-lg bg-white px-3 py-2 text-[10px] font-bold text-slate-600 shadow-lg">
            Còn khoảng 22 phút
          </div>
        </div>
        <div className="p-5">
          <h3 className="text-sm font-bold text-slate-800">{active.dealer}</h3>
          <p className="mt-1 text-xs text-slate-400">{active.address}</p>
          <button
            onClick={() => notify("Đã gửi yêu cầu liên hệ đến tài xế Nguyễn Minh")}
            className="secondary-button mt-4"
          >
            Liên hệ tài xế
          </button>
        </div>
      </section>
      <aside className="panel h-fit p-5">
        <h3 className="text-sm font-bold text-slate-900">Tiến trình đơn hàng</h3>
        <div className="mt-5 space-y-0">
          {steps.map((step, index) => (
            <div key={step} className="flex gap-3">
              <div className="flex flex-col items-center">
                <span
                  className={`grid size-7 place-items-center rounded-full ${index < currentStep ? "bg-emerald-600 text-white" : "bg-slate-100 text-slate-400"}`}
                >
                  {index < currentStep ? <Check size={14} /> : index + 1}
                </span>
                {index < steps.length - 1 && (
                  <i
                    className={`h-10 w-0.5 ${index < currentStep - 1 ? "bg-emerald-500" : "bg-slate-200"}`}
                  />
                )}
              </div>
              <div className="pt-1">
                <p
                  className={`text-xs font-bold ${index < currentStep ? "text-slate-800" : "text-slate-400"}`}
                >
                  {step}
                </p>
                {index < currentStep && (
                  <p className="mt-0.5 text-[9px] text-slate-400">Đã cập nhật</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
}

const supplyStatusStyle: Record<SupplyStatus, string> = {
  "Chờ phản hồi": "bg-amber-50 text-amber-700",
  "Đã xác nhận": "bg-blue-50 text-blue-700",
  "Đang vận chuyển": "bg-violet-50 text-violet-700",
  "Đã nhập kho": "bg-emerald-50 text-emerald-700",
  "Đã từ chối": "bg-rose-50 text-rose-700",
};

function SupplyBadge({ status }: { status: SupplyStatus }) {
  return (
    <span
      className={`whitespace-nowrap rounded-full px-2.5 py-1 text-[10px] font-bold ${supplyStatusStyle[status]}`}
    >
      {status}
    </span>
  );
}

function SupplierApp({
  requests,
  setRequests,
  notify,
}: {
  requests: SupplyRequest[];
  setRequests: React.Dispatch<React.SetStateAction<SupplyRequest[]>>;
  notify: (s: string) => void;
}) {
  const [page, setPage] = useState("Tổng quan");
  const [menu, setMenu] = useState(false);
  const [viewing, setViewing] = useState<SupplyRequest | null>(null);
  const [query, setQuery] = useState("");
  const nav: [string, LucideIcon][] = [
    ["Tổng quan", LayoutDashboard],
    ["Yêu cầu cung ứng", ClipboardList],
    ["Lịch giao hàng", Truck],
    ["Sản phẩm", Boxes],
    ["Tài khoản", UserRound],
  ];
  const updateStatus = (id: string, status: SupplyStatus) => {
    setRequests((current) => current.map((item) => (item.id === id ? { ...item, status } : item)));
    setViewing(null);
    notify(
      status === "Đang vận chuyển"
        ? `Đã xuất hàng cho phiếu ${id}`
        : `${status} yêu cầu cung ứng ${id}`,
    );
  };

  return (
    <div className="supplier-shell min-h-screen pb-24 md:pb-0">
      {menu && (
        <button
          aria-label="Đóng menu"
          onClick={() => setMenu(false)}
          className="fixed inset-0 z-30 bg-slate-950/35 md:hidden"
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-[248px] flex-col bg-slate-950 text-white transition-transform md:translate-x-0 ${menu ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="flex h-18 items-center border-b border-white/10 px-5">
          <Logo dark />
        </div>
        <div className="px-4 pt-5">
          <div className="rounded-xl border border-violet-400/20 bg-violet-400/10 p-3">
            <p className="text-[9px] font-bold uppercase tracking-[.14em] text-violet-300">
              Nhà cung cấp
            </p>
            <p className="mt-1 text-xs font-bold">Công ty Lavie Việt Nam</p>
            <p className="mt-1 text-[9px] text-slate-400">Mã NCC: NCC-0012</p>
          </div>
        </div>
        <nav className="flex-1 px-3 py-4">
          {nav.map(([label, Icon]) => (
            <button
              key={label}
              onClick={() => {
                setPage(label);
                setMenu(false);
              }}
              className={`mb-1 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-xs font-semibold ${page === label ? "bg-violet-600 text-white" : "text-slate-400 hover:bg-white/5 hover:text-white"}`}
            >
              <Icon size={17} />
              {label}
              {label === "Yêu cầu cung ứng" &&
                requests.some((r) => r.status === "Chờ phản hồi") && (
                  <span className="ml-auto grid size-5 place-items-center rounded-full bg-amber-400 text-[9px] font-extrabold text-slate-950">
                    {requests.filter((r) => r.status === "Chờ phản hồi").length}
                  </span>
                )}
            </button>
          ))}
        </nav>
        <div className="m-3 flex items-center gap-3 rounded-xl border border-white/10 p-3">
          <span className="grid size-9 place-items-center rounded-lg bg-violet-600 text-xs font-bold">
            LV
          </span>
          <div>
            <p className="text-xs font-bold">Lan Vy</p>
            <p className="text-[9px] text-slate-400">Điều phối cung ứng</p>
          </div>
        </div>
      </aside>

      <div className="md:pl-[248px]">
        <header className="sticky top-0 z-20 flex h-18 items-center justify-between border-b border-violet-100 bg-white/85 px-4 shadow-[0_4px_24px_rgba(124,58,237,0.06)] backdrop-blur-xl sm:px-7">
          <div className="flex items-center gap-3">
            <button onClick={() => setMenu(true)} className="icon-button md:hidden">
              <Menu size={19} />
            </button>
            <div>
              <p className="text-[10px] text-slate-400">Cổng Nhà cung cấp / {page}</p>
              <h1 className="text-lg font-bold">{page}</h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => notify("Đã xuất báo cáo nhà cung cấp tháng 6")}
              className="secondary-button hidden sm:flex"
            >
              <Download size={14} /> Xuất báo cáo
            </button>
            <button
              onClick={() => notify("Bạn có 2 thông báo cung ứng mới")}
              className="icon-button relative"
            >
              <Bell size={17} />
              <i className="absolute right-2 top-2 size-1.5 rounded-full bg-violet-500" />
            </button>
          </div>
        </header>

        <main className="mx-auto max-w-[1500px] p-4 sm:p-7">
          {page === "Tổng quan" ? (
            <SupplierDashboard
              requests={requests}
              openRequest={(request) => setViewing(request)}
              goTo={setPage}
              notify={notify}
            />
          ) : page === "Yêu cầu cung ứng" ? (
            <SupplierRequests
              requests={requests}
              query={query}
              setQuery={setQuery}
              openRequest={setViewing}
              updateStatus={updateStatus}
            />
          ) : page === "Lịch giao hàng" ? (
            <SupplierSchedule requests={requests} updateStatus={updateStatus} notify={notify} />
          ) : page === "Sản phẩm" ? (
            <SupplierProducts notify={notify} />
          ) : (
            <SupplierProfile notify={notify} />
          )}
        </main>
      </div>

      <nav className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-5 border-t border-slate-200 bg-white px-1 pb-[max(8px,env(safe-area-inset-bottom))] pt-2 md:hidden">
        {nav.map(([label, Icon]) => (
          <button
            key={label}
            onClick={() => setPage(label)}
            className={`flex flex-col items-center gap-1 py-1 text-[8px] font-semibold ${page === label ? "text-violet-600" : "text-slate-400"}`}
          >
            <Icon size={18} />
            {label === "Yêu cầu cung ứng"
              ? "Yêu cầu"
              : label === "Lịch giao hàng"
                ? "Lịch giao"
                : label}
          </button>
        ))}
      </nav>
      {viewing && (
        <SupplyRequestModal
          request={viewing}
          close={() => setViewing(null)}
          updateStatus={updateStatus}
        />
      )}
    </div>
  );
}

function SupplierDashboard({
  requests,
  openRequest,
  goTo,
  notify,
}: {
  requests: SupplyRequest[];
  openRequest: (request: SupplyRequest) => void;
  goTo: (page: string) => void;
  notify: (s: string) => void;
}) {
  const awaiting = requests.filter((r) => r.status === "Chờ phản hồi").length;
  const revenue = requests
    .filter((r) => r.status !== "Đã từ chối")
    .reduce((sum, r) => sum + r.value, 0);
  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-2xl bg-gradient-to-br from-violet-700 via-violet-600 to-indigo-600 p-6 text-white shadow-lg shadow-violet-600/15 sm:p-8">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs font-semibold text-violet-200">Thứ 2, 29 tháng 6</p>
            <h2 className="mt-2 text-2xl font-bold">Chào buổi sáng, Lan Vy</h2>
            <p className="mt-2 max-w-xl text-sm text-violet-100">
              Có {awaiting} yêu cầu mới cần phản hồi để kho chủ động kế hoạch nhập hàng.
            </p>
          </div>
          <button
            onClick={() => goTo("Yêu cầu cung ứng")}
            className="flex w-fit items-center gap-2 rounded-xl bg-white px-4 py-3 text-xs font-bold text-violet-700 shadow-lg"
          >
            Xử lý yêu cầu <ArrowRight size={15} />
          </button>
        </div>
      </section>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[
          [ClipboardList, String(awaiting), "Chờ phản hồi", "text-amber-600 bg-amber-50"],
          [
            Truck,
            String(requests.filter((r) => r.status === "Đang vận chuyển").length),
            "Đang vận chuyển",
            "text-violet-600 bg-violet-50",
          ],
          [
            PackageCheck,
            requests.reduce((s, r) => s + r.qty, 0).toLocaleString("vi-VN"),
            "Thùng đã đặt",
            "text-blue-600 bg-blue-50",
          ],
          [
            CircleDollarSign,
            formatMoney(revenue),
            "Giá trị cung ứng",
            "text-emerald-600 bg-emerald-50",
          ],
        ].map(([Icon, value, label, color]) => (
          <div
            key={label as string}
            className="panel bg-gradient-to-br from-white to-violet-50/50 p-5"
          >
            <span className={`grid size-10 place-items-center rounded-xl ${color as string}`}>
              <Icon size={19} />
            </span>
            <p className="mt-4 text-xl font-extrabold text-slate-900">{value as string}</p>
            <p className="mt-1 text-[10px] text-slate-400">{label as string}</p>
          </div>
        ))}
      </div>
      <div className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
        <section className="panel overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-100 p-5">
            <div>
              <h3 className="section-title">Yêu cầu gần đây</h3>
              <p className="section-subtitle">Đồng bộ từ Quản lý kho DistriFlow</p>
            </div>
            <button onClick={() => goTo("Yêu cầu cung ứng")} className="text-button">
              Xem tất cả <ArrowRight size={13} />
            </button>
          </div>
          <div className="divide-y divide-slate-100">
            {requests.slice(0, 3).map((r) => (
              <button
                key={r.id}
                onClick={() => openRequest(r)}
                className="flex w-full items-center gap-3 p-4 text-left hover:bg-slate-50"
              >
                <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-violet-50 text-violet-600">
                  <Package size={18} />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-[10px] font-bold text-violet-600">{r.id}</p>
                  <p className="truncate text-xs font-bold text-slate-800">{r.product}</p>
                  <p className="text-[9px] text-slate-400">
                    {r.qty.toLocaleString("vi-VN")} thùng • trước {r.due}
                  </p>
                </div>
                <SupplyBadge status={r.status} />
                <ChevronRight size={15} className="text-slate-300" />
              </button>
            ))}
          </div>
        </section>
        <section className="panel p-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="section-title">Hiệu suất tháng 6</h3>
              <p className="section-subtitle">Cam kết dịch vụ nhà cung cấp</p>
            </div>
            <Activity size={18} className="text-violet-600" />
          </div>
          <div className="mt-5 space-y-4">
            {[
              ["Giao đúng hạn", "96%", "w-[96%]"],
              ["Đủ số lượng", "99%", "w-[99%]"],
              ["Chất lượng đạt", "98%", "w-[98%]"],
            ].map(([label, value, width]) => (
              <div key={label}>
                <div className="mb-1.5 flex justify-between text-[10px]">
                  <span className="font-semibold text-slate-600">{label}</span>
                  <b>{value}</b>
                </div>
                <div className="h-1.5 rounded-full bg-slate-100">
                  <div className={`h-full rounded-full bg-violet-600 ${width}`} />
                </div>
              </div>
            ))}
          </div>
          <button
            onClick={() => notify("Đã tải phiếu đánh giá nhà cung cấp tháng 6")}
            className="secondary-button mt-6 w-full justify-center"
          >
            <FileText size={14} /> Phiếu đánh giá
          </button>
        </section>
      </div>
    </div>
  );
}

function SupplierRequests({
  requests,
  query,
  setQuery,
  openRequest,
  updateStatus,
}: {
  requests: SupplyRequest[];
  query: string;
  setQuery: (query: string) => void;
  openRequest: (request: SupplyRequest) => void;
  updateStatus: (id: string, status: SupplyStatus) => void;
}) {
  const [filter, setFilter] = useState("Tất cả");
  const shown = requests.filter(
    (r) =>
      `${r.id} ${r.product} ${r.sku}`.toLowerCase().includes(query.toLowerCase()) &&
      (filter === "Tất cả" || r.status === filter),
  );
  return (
    <section className="panel overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-slate-100 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="section-title">Danh sách yêu cầu cung ứng</h2>
          <p className="section-subtitle">{shown.length} yêu cầu phù hợp</p>
        </div>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="input pl-9"
              placeholder="Tìm mã, sản phẩm..."
            />
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="secondary-button max-w-36"
          >
            <option>Tất cả</option>
            {Object.keys(supplyStatusStyle).map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="data-table min-w-[850px]">
          <thead>
            <tr>
              <th>Mã yêu cầu</th>
              <th>Sản phẩm</th>
              <th>Số lượng</th>
              <th>Hạn giao</th>
              <th>Giá trị</th>
              <th>Trạng thái</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {shown.map((r) => (
              <tr key={r.id}>
                <td>
                  <button
                    onClick={() => openRequest(r)}
                    className="font-mono font-bold text-violet-600"
                  >
                    {r.id}
                  </button>
                </td>
                <td>
                  <b className="text-slate-700">{r.product}</b>
                  <p className="mt-0.5 text-[9px] text-slate-400">{r.sku}</p>
                </td>
                <td>{r.qty.toLocaleString("vi-VN")} thùng</td>
                <td>{r.due}</td>
                <td className="font-semibold">{formatMoney(r.value)}</td>
                <td>
                  <SupplyBadge status={r.status} />
                </td>
                <td>
                  <div className="flex justify-end gap-2">
                    {r.status === "Chờ phản hồi" ? (
                      <>
                        <button
                          onClick={() => updateStatus(r.id, "Đã từ chối")}
                          className="text-[10px] font-bold text-rose-600"
                        >
                          Từ chối
                        </button>
                        <button
                          onClick={() => updateStatus(r.id, "Đã xác nhận")}
                          className="rounded-lg bg-violet-600 px-3 py-2 text-[10px] font-bold text-white"
                        >
                          Xác nhận
                        </button>
                      </>
                    ) : (
                      <button onClick={() => openRequest(r)} className="secondary-button h-8">
                        Chi tiết
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!shown.length && (
        <div className="grid h-44 place-items-center text-sm text-slate-400">
          Không tìm thấy yêu cầu phù hợp
        </div>
      )}
    </section>
  );
}

function SupplierSchedule({
  requests,
  updateStatus,
  notify,
}: {
  requests: SupplyRequest[];
  updateStatus: (id: string, status: SupplyStatus) => void;
  notify: (s: string) => void;
}) {
  const scheduled = requests.filter((r) =>
    ["Đã xác nhận", "Đang vận chuyển", "Đã nhập kho"].includes(r.status),
  );
  return (
    <div className="grid gap-5 lg:grid-cols-[1.4fr_1fr]">
      <section className="panel overflow-hidden">
        <div className="border-b border-slate-100 p-5">
          <h2 className="section-title">Lịch giao hàng sắp tới</h2>
          <p className="section-subtitle">Chuẩn bị hàng và chứng từ theo từng lịch hẹn</p>
        </div>
        <div className="divide-y divide-slate-100">
          {scheduled.map((r, index) => (
            <div key={r.id} className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center">
              <div className="grid size-14 shrink-0 place-items-center rounded-xl bg-violet-50 text-center">
                <b className="text-sm text-violet-700">{r.due.slice(0, 2)}</b>
                <span className="-mt-2 text-[8px] font-bold text-violet-400">
                  THÁNG {r.due.slice(3, 5)}
                </span>
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="text-[10px] font-bold text-violet-600">{r.id}</p>
                  <SupplyBadge status={r.status} />
                </div>
                <h3 className="mt-1 text-sm font-bold">{r.product}</h3>
                <p className="mt-1 text-[10px] text-slate-400">
                  {r.qty.toLocaleString("vi-VN")} thùng • {r.warehouse}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => notify(`Đã tải phiếu giao hàng ${r.id}`)}
                  className="icon-button border-slate-200"
                >
                  <Download size={15} />
                </button>
                {r.status === "Đã xác nhận" && (
                  <button
                    onClick={() => updateStatus(r.id, "Đang vận chuyển")}
                    className="rounded-lg bg-violet-600 px-3 py-2 text-[10px] font-bold text-white"
                  >
                    Xác nhận xuất hàng
                  </button>
                )}
                {index === 0 && r.status === "Đang vận chuyển" && (
                  <button
                    onClick={() => notify(`Đang theo dõi xe giao phiếu ${r.id}`)}
                    className="secondary-button"
                  >
                    Theo dõi
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
      <aside className="panel h-fit p-5">
        <h3 className="section-title">Checklist giao hàng</h3>
        <p className="section-subtitle">Hoàn tất trước khi xe rời kho</p>
        <div className="mt-5 space-y-3">
          {[
            "Đóng gói và dán mã kiện",
            "Kiểm đếm đủ số lượng",
            "Phiếu xuất kho & hóa đơn",
            "Xác nhận biển số xe",
          ].map((item, i) => (
            <label
              key={item}
              className="flex items-center gap-3 rounded-lg bg-slate-50 p-3 text-xs font-semibold text-slate-600"
            >
              <input type="checkbox" defaultChecked={i < 2} className="accent-violet-600" />
              {item}
            </label>
          ))}
        </div>
        <button
          onClick={() => notify("Đã lưu checklist chuẩn bị giao hàng")}
          className="mt-4 w-full rounded-lg bg-slate-900 py-2.5 text-xs font-bold text-white"
        >
          Lưu checklist
        </button>
      </aside>
    </div>
  );
}

function SupplierProducts({ notify }: { notify: (s: string) => void }) {
  const [stocks, setStocks] = useState(() =>
    products.slice(0, 4).map((p) => ({ ...p, supplierStock: Math.round(p.stock * 1.8) })),
  );
  const [editing, setEditing] = useState<number | null>(null);
  return (
    <section className="panel overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-100 p-5">
        <div>
          <h2 className="section-title">Danh mục cung ứng</h2>
          <p className="section-subtitle">Cập nhật tồn khả dụng để Quản lý kho lập kế hoạch</p>
        </div>
        <button
          onClick={() => notify("Danh mục đã đồng bộ với DistriFlow")}
          className="secondary-button"
        >
          <Activity size={14} /> Đồng bộ
        </button>
      </div>
      <div className="grid gap-4 p-4 sm:grid-cols-2 xl:grid-cols-3">
        {stocks.map((p) => (
          <article key={p.id} className="rounded-xl border border-slate-200 p-4">
            <div className="flex gap-3">
              <img src={p.image} alt={p.name} className="size-14 rounded-xl object-cover" />
              <div className="min-w-0">
                <p className="text-[9px] font-bold text-violet-600">{p.sku}</p>
                <h3 className="mt-1 truncate text-xs font-bold">{p.name}</h3>
                <p className="mt-1 text-[10px] text-slate-400">{p.category}</p>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between rounded-lg bg-slate-50 p-3">
              <div>
                <p className="text-[9px] text-slate-400">Tồn khả dụng</p>
                {editing === p.id ? (
                  <input
                    autoFocus
                    type="number"
                    defaultValue={p.supplierStock}
                    onBlur={(e) => {
                      setStocks((current) =>
                        current.map((x) =>
                          x.id === p.id ? { ...x, supplierStock: Number(e.target.value) } : x,
                        ),
                      );
                      setEditing(null);
                      notify(`Đã cập nhật tồn ${p.name}`);
                    }}
                    className="mt-1 w-24 rounded border border-violet-300 bg-white px-2 py-1 text-sm font-bold outline-none"
                  />
                ) : (
                  <b className="text-sm">{p.supplierStock.toLocaleString("vi-VN")} thùng</b>
                )}
              </div>
              <button onClick={() => setEditing(p.id)} className="icon-button">
                <Pencil size={14} />
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function SupplierProfile({ notify }: { notify: (s: string) => void }) {
  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <section className="panel p-6">
        <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
          <span className="grid size-16 place-items-center rounded-2xl bg-violet-100 text-xl font-extrabold text-violet-700">
            LV
          </span>
          <div className="flex-1">
            <h2 className="text-lg font-bold">Công ty Lavie Việt Nam</h2>
            <p className="mt-1 text-xs text-slate-400">MST 0100101849 • Đối tác từ 2021</p>
          </div>
          <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700">
            Đã xác minh
          </span>
        </div>
      </section>
      <section className="panel overflow-hidden">
        {[
          ["Thông tin doanh nghiệp", "Hồ sơ, địa chỉ và người đại diện"],
          ["Tài khoản ngân hàng", "Vietcombank •••• 8826"],
          ["Thông báo", "Email, SMS và ứng dụng"],
          ["Hợp đồng điện tử", "HĐ-DF-2025-012"],
        ].map(([title, meta]) => (
          <button
            key={title}
            onClick={() => notify(`Đang mở ${title.toLowerCase()}`)}
            className="flex w-full items-center gap-3 border-b border-slate-100 p-4 text-left last:border-0 hover:bg-slate-50"
          >
            <span className="grid size-9 place-items-center rounded-lg bg-violet-50 text-violet-600">
              <FileText size={16} />
            </span>
            <div className="flex-1">
              <p className="text-xs font-bold">{title}</p>
              <p className="mt-0.5 text-[10px] text-slate-400">{meta}</p>
            </div>
            <ChevronRight size={16} className="text-slate-300" />
          </button>
        ))}
      </section>
      <button
        onClick={() => notify("Đây là tài khoản demo — phiên đăng nhập được giữ nguyên")}
        className="secondary-button w-full justify-center text-rose-600"
      >
        <LogOut size={15} /> Đăng xuất
      </button>
    </div>
  );
}

function SupplyRequestModal({
  request,
  close,
  updateStatus,
}: {
  request: SupplyRequest;
  close: () => void;
  updateStatus: (id: string, status: SupplyStatus) => void;
}) {
  return (
    <div className="fixed inset-0 z-[90] grid place-items-center bg-slate-950/45 p-4 backdrop-blur-sm">
      <button aria-label="Đóng" onClick={close} className="absolute inset-0" />
      <div className="relative w-full max-w-lg rounded-2xl bg-white shadow-2xl">
        <div className="flex items-start justify-between border-b border-slate-100 p-5">
          <div>
            <p className="text-[10px] font-bold text-violet-600">{request.id}</p>
            <h3 className="mt-1 text-lg font-bold">{request.product}</h3>
          </div>
          <button onClick={close} className="icon-button">
            <X size={18} />
          </button>
        </div>
        <div className="grid gap-3 p-5 sm:grid-cols-2">
          {[
            ["Mã SKU", request.sku],
            ["Số lượng", `${request.qty.toLocaleString("vi-VN")} thùng`],
            ["Hạn giao", request.due],
            ["Giá trị", formatMoney(request.value)],
            ["Kho nhận", request.warehouse],
            ["Trạng thái", request.status],
          ].map(([label, value]) => (
            <div key={label} className={label === "Kho nhận" ? "sm:col-span-2" : ""}>
              <p className="text-[9px] font-bold uppercase tracking-wider text-slate-400">
                {label}
              </p>
              <p className="mt-1 text-xs font-semibold text-slate-700">{value}</p>
            </div>
          ))}
        </div>
        <div className="flex justify-end gap-2 border-t border-slate-100 p-4">
          <button onClick={close} className="secondary-button">
            Đóng
          </button>
          {request.status === "Chờ phản hồi" && (
            <>
              <button
                onClick={() => updateStatus(request.id, "Đã từ chối")}
                className="secondary-button text-rose-600"
              >
                Từ chối
              </button>
              <button
                onClick={() => updateStatus(request.id, "Đã xác nhận")}
                className="rounded-lg bg-violet-600 px-4 text-xs font-bold text-white"
              >
                Xác nhận cung ứng
              </button>
            </>
          )}
          {request.status === "Đã xác nhận" && (
            <button
              onClick={() => updateStatus(request.id, "Đang vận chuyển")}
              className="rounded-lg bg-violet-600 px-4 text-xs font-bold text-white"
            >
              Xác nhận xuất hàng
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function ShipperApp({
  orders,
  setOrders,
  notify,
}: {
  orders: Order[];
  setOrders: React.Dispatch<React.SetStateAction<Order[]>>;
  notify: (s: string) => void;
}) {
  const [page, setPage] = useState("Trang chủ");
  const [activeId, setActiveId] = useState(
    orders.find((o) => o.status === "Đang giao")?.id || orders[0]?.id,
  );
  const active = orders.find((o) => o.id === activeId) || orders[0];
  const deliveries = orders.filter((o) =>
    ["Đã duyệt", "Đang giao", "Hoàn thành"].includes(o.status),
  );
  const change = (status: OrderStatus) => {
    setOrders((o) => o.map((x) => (x.id === active.id ? { ...x, status } : x)));
    notify(
      status === "Hoàn thành" ? "Đã xác nhận giao hàng thành công" : `Đã nhận chuyến ${active.id}`,
    );
  };
  return (
    <div className="shipper-shell min-h-screen pb-24">
      <div className="mx-auto min-h-screen max-w-[480px] bg-white/70 shadow-2xl shadow-orange-950/10 backdrop-blur-sm">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between bg-slate-950 px-4 text-white">
          <Logo dark />
          <div className="flex items-center gap-1">
            <button
              onClick={() => notify("Bạn có 3 thông báo chuyến giao mới")}
              className="relative grid size-9 place-items-center rounded-full bg-white/10"
            >
              <Bell size={17} />
              <i className="absolute right-2 top-2 size-1.5 rounded-full bg-orange-500" />
            </button>
            <div className="ml-1 grid size-9 place-items-center rounded-full bg-orange-600 text-xs font-bold">
              NM
            </div>
          </div>
        </header>
        <main className="px-4 py-5">
          {page === "Trang chủ" ? (
            <ShipperDashboard
              deliveries={deliveries}
              open={(id) => {
                setActiveId(id);
                setPage("Chuyến giao");
              }}
            />
          ) : page === "Chuyến giao" ? (
            <DeliveryDetail
              order={active}
              change={change}
              notify={notify}
              onBack={() => setPage("Trang chủ")}
            />
          ) : page === "Lịch sử" ? (
            <ShipperHistory orders={orders} />
          ) : (
            <ShipperProfile notify={notify} />
          )}
        </main>
        <nav className="fixed inset-x-0 bottom-0 z-30 mx-auto grid max-w-[480px] grid-cols-4 border-t border-slate-200 bg-white px-2 pb-[max(8px,env(safe-area-inset-bottom))] pt-2">
          {[
            ["Trang chủ", LayoutDashboard],
            ["Chuyến giao", Truck],
            ["Lịch sử", History],
            ["Tài khoản", UserRound],
          ].map(([n, I]) => (
            <button
              key={n as string}
              onClick={() => setPage(n as string)}
              className={`relative flex flex-col items-center gap-1 py-1 text-[10px] font-semibold ${page === n ? "text-orange-600" : "text-slate-400"}`}
            >
              <I size={19} strokeWidth={page === n ? 2.5 : 1.8} />
              {n as string}
              {n === "Chuyến giao" && (
                <span className="absolute right-[25%] top-0 size-2 rounded-full bg-orange-500 ring-2 ring-white" />
              )}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}

function ShipperDashboard({
  deliveries,
  open,
}: {
  deliveries: Order[];
  open: (id: string) => void;
}) {
  const [showAll, setShowAll] = useState(false);
  return (
    <>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-400">Thứ 2, 29 tháng 6</p>
          <h1 className="mt-1 text-xl font-bold text-slate-900">Chào Nguyễn Minh!</h1>
        </div>
        <span className="flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-bold text-emerald-700">
          <i className="size-1.5 rounded-full bg-emerald-500" />
          Đang hoạt động
        </span>
      </div>
      <section className="mt-5 overflow-hidden rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 p-5 text-white shadow-lg shadow-orange-600/20">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-orange-100">Tiến độ hôm nay</p>
            <p className="mt-1 text-3xl font-extrabold">
              4 <span className="text-base font-medium text-orange-100">/ 7 điểm</span>
            </p>
          </div>
          <div className="grid size-11 place-items-center rounded-xl bg-white/15">
            <Navigation size={22} />
          </div>
        </div>
        <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-white/20">
          <div className="h-full w-[57%] rounded-full bg-white" />
        </div>
        <div className="mt-3 flex justify-between text-[10px] text-orange-100">
          <span>Đã giao 4 đơn</span>
          <span>Còn lại 3 đơn</span>
        </div>
      </section>
      <div className="mt-5 grid grid-cols-3 gap-2">
        {[
          [PackageCheck, "12", "Đơn đã giao"],
          [MapPin, "38 km", "Quãng đường"],
          [Clock3, "6h20", "Hoạt động"],
        ].map(([I, v, l]) => (
          <div key={l as string} className="rounded-xl border border-slate-200 bg-white p-3">
            <I size={17} className="text-orange-600" />
            <p className="mt-2 text-sm font-extrabold text-slate-900">{v as string}</p>
            <p className="text-[9px] text-slate-400">{l as string}</p>
          </div>
        ))}
      </div>
      <div className="mt-6 flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-900">Chuyến giao tiếp theo</h2>
          <p className="text-[10px] text-slate-400">{deliveries.length} đơn được phân công</p>
        </div>
        <button
          onClick={() => setShowAll((value) => !value)}
          className="text-xs font-bold text-orange-600"
        >
          {showAll ? "Thu gọn" : "Xem tất cả"}
        </button>
      </div>
      <div className="mt-3 space-y-3">
        {deliveries.slice(0, showAll ? deliveries.length : 3).map((o, i) => (
          <button
            key={o.id}
            onClick={() => open(o.id)}
            className="w-full rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm"
          >
            <div className="flex items-start gap-3">
              <span
                className={`grid size-9 shrink-0 place-items-center rounded-full text-xs font-extrabold ${i === 0 ? "bg-orange-600 text-white" : "bg-slate-100 text-slate-500"}`}
              >
                {i + 1}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex justify-between">
                  <p className="text-[10px] font-bold text-orange-600">{o.id}</p>
                  <Status value={o.status} />
                </div>
                <h3 className="mt-1 truncate text-sm font-bold text-slate-800">{o.dealer}</h3>
                <p className="mt-1 flex items-center gap-1 truncate text-[10px] text-slate-400">
                  <MapPin size={11} />
                  {o.address}
                </p>
              </div>
              <ChevronRight size={17} className="mt-5 text-slate-300" />
            </div>
          </button>
        ))}
      </div>
    </>
  );
}

function DeliveryDetail({
  order,
  change,
  notify,
  onBack,
}: {
  order: Order;
  change: (s: OrderStatus) => void;
  notify: (s: string) => void;
  onBack: () => void;
}) {
  const [scanned, setScanned] = useState(false);
  const [signed, setSigned] = useState(false);
  return (
    <>
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="icon-button">
          <ChevronLeft size={18} />
        </button>
        <div>
          <p className="text-[10px] font-bold text-orange-600">{order.id}</p>
          <h1 className="text-lg font-bold text-slate-900">Chi tiết chuyến giao</h1>
        </div>
        <Status value={order.status} />
      </div>
      <section className="relative mt-4 h-44 overflow-hidden rounded-2xl border border-slate-200 bg-[#E8EEE8]">
        <div
          className="absolute inset-0 opacity-60"
          style={{
            backgroundImage:
              "linear-gradient(30deg, transparent 48%, #cbd5e1 49%, #cbd5e1 51%, transparent 52%),linear-gradient(120deg, transparent 48%, #cbd5e1 49%, #cbd5e1 51%, transparent 52%)",
            backgroundSize: "60px 60px",
          }}
        />
        <svg className="absolute inset-0 size-full" viewBox="0 0 400 180">
          <path
            d="M35 145 C100 110,110 40,180 70 S280 140,365 38"
            fill="none"
            stroke="#EA580C"
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray="7 7"
          />
        </svg>
        <span className="absolute bottom-5 left-7 grid size-8 place-items-center rounded-full bg-slate-900 text-white ring-4 ring-white">
          <Navigation size={15} />
        </span>
        <span className="absolute right-5 top-5 grid size-9 place-items-center rounded-full bg-orange-600 text-white ring-4 ring-white">
          <MapPin size={17} />
        </span>
        <button
          onClick={() => notify("Đã mở chỉ đường đến điểm giao")}
          className="absolute bottom-3 right-3 flex items-center gap-1.5 rounded-lg bg-white px-3 py-2 text-[10px] font-bold text-slate-700 shadow-lg"
        >
          <Map size={13} />
          Mở chỉ đường
        </button>
      </section>
      <section className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
        <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Điểm giao</p>
        <h2 className="mt-2 text-base font-bold text-slate-900">{order.dealer}</h2>
        <p className="mt-1 text-xs leading-5 text-slate-500">{order.address}</p>
        <div className="mt-4 flex gap-2">
          <button
            onClick={() => notify("Đang gọi cho khách hàng...")}
            className="secondary-button flex-1 justify-center"
          >
            Gọi khách hàng
          </button>
          <button
            onClick={() => notify("Đã mở khung nhắn tin với khách hàng")}
            className="secondary-button flex-1 justify-center"
          >
            Nhắn tin
          </button>
        </div>
      </section>
      <section className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-bold text-slate-800">Kiểm tra hàng hóa</p>
            <p className="text-[10px] text-slate-400">{order.items} kiện cần bàn giao</p>
          </div>
          <button
            onClick={() => {
              setScanned(true);
              notify("Quét mã thành công — đủ số lượng");
            }}
            className={`grid size-10 place-items-center rounded-xl ${scanned ? "bg-emerald-50 text-emerald-600" : "bg-orange-50 text-orange-600"}`}
          >
            {scanned ? <CheckCircle2 size={20} /> : <QrCode size={20} />}
          </button>
        </div>
        {scanned && (
          <p className="mt-3 rounded-lg bg-emerald-50 p-2.5 text-[11px] font-semibold text-emerald-700">
            Đã quét đủ {order.items}/{order.items} kiện hàng
          </p>
        )}
      </section>
      {order.status === "Đã duyệt" ? (
        <button
          onClick={() => change("Đang giao")}
          className="mt-4 w-full rounded-xl bg-orange-600 py-3.5 text-sm font-bold text-white shadow-lg shadow-orange-600/20"
        >
          Nhận chuyến giao
        </button>
      ) : order.status === "Đang giao" ? (
        <>
          <label className="mt-4 flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 text-xs font-semibold text-slate-700">
            <input
              type="checkbox"
              checked={signed}
              onChange={(e) => setSigned(e.target.checked)}
              className="accent-orange-600"
            />
            Khách hàng đã ký nhận đầy đủ
          </label>
          <button
            disabled={!scanned || !signed}
            onClick={() => change("Hoàn thành")}
            className="mt-3 w-full rounded-xl bg-orange-600 py-3.5 text-sm font-bold text-white shadow-lg shadow-orange-600/20 disabled:opacity-40"
          >
            Xác nhận giao thành công
          </button>
        </>
      ) : (
        <div className="mt-4 rounded-xl bg-emerald-50 p-4 text-center text-sm font-bold text-emerald-700">
          <CheckCircle2 className="mx-auto mb-2" size={26} />
          Đơn hàng đã hoàn thành
        </div>
      )}
    </>
  );
}

function ShipperHistory({ orders }: { orders: Order[] }) {
  return (
    <>
      <h1 className="text-xl font-bold text-slate-900">Lịch sử giao hàng</h1>
      <p className="mt-1 text-xs text-slate-400">Tổng hợp các chuyến đã hoàn thành</p>
      <div className="mt-5 space-y-3">
        {orders
          .filter((o) => o.status === "Hoàn thành")
          .map((o) => (
            <div key={o.id} className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex justify-between">
                <b className="text-xs text-slate-800">{o.id}</b>
                <Status value={o.status} />
              </div>
              <p className="mt-2 text-sm font-semibold">{o.dealer}</p>
              <p className="mt-1 text-[10px] text-slate-400">{o.address}</p>
            </div>
          ))}
      </div>
    </>
  );
}
function ShipperProfile({ notify }: { notify: (s: string) => void }) {
  return (
    <>
      <h1 className="text-xl font-bold text-slate-900">Tài khoản</h1>
      <div className="mt-5 rounded-2xl border border-slate-200 bg-white p-5 text-center">
        <div className="mx-auto grid size-20 place-items-center rounded-full bg-orange-100 text-xl font-bold text-orange-700">
          NM
        </div>
        <h2 className="mt-3 text-lg font-bold">Nguyễn Minh</h2>
        <p className="text-xs text-slate-400">Tài xế • 59C1-123.45</p>
        <div className="mt-5 grid grid-cols-2 gap-2">
          <div className="rounded-xl bg-slate-50 p-3">
            <b className="text-lg">4.9</b>
            <p className="text-[10px] text-slate-400">Điểm đánh giá</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-3">
            <b className="text-lg">284</b>
            <p className="text-[10px] text-slate-400">Chuyến đã giao</p>
          </div>
        </div>
      </div>
      <button
        onClick={() => notify("Đây là tài khoản demo — phiên đăng nhập được giữ nguyên")}
        className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-red-200 bg-white py-3 text-sm font-bold text-red-600"
      >
        <LogOut size={17} />
        Đăng xuất
      </button>
    </>
  );
}

export default function App() {
  const [mode, setMode] = useState<AppMode>("admin");
  const [orders, setOrders] = useState<Order[]>(initialOrders);
  const [supplyRequests, setSupplyRequests] = useState<SupplyRequest[]>(initialSupplyRequests);
  const [toast, setToast] = useState("");
  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2800);
  };
  return (
    <>
      {mode === "supplier" ? (
        <SupplierApp requests={supplyRequests} setRequests={setSupplyRequests} notify={notify} />
      ) : mode === "admin" ? (
        <AdminApp orders={orders} setOrders={setOrders} notify={notify} />
      ) : mode === "partner" ? (
        <PartnerApp orders={orders} setOrders={setOrders} notify={notify} />
      ) : (
        <ShipperApp orders={orders} setOrders={setOrders} notify={notify} />
      )}
      <DemoSwitcher mode={mode} setMode={setMode} />
      {toast && <Toast message={toast} />}
    </>
  );
}
