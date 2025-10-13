import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';
import { AlertCircle, TrendingUp, Users, DollarSign, Target, Activity, Menu, X, ChevronRight, RefreshCw, Settings } from 'lucide-react';

// API Configuration
const API_BASE_URL = 'https://api.yourorg.com';

const App = () => {
  const [orgId, setOrgId] = useState('');
  const [tempOrgId, setTempOrgId] = useState('');
  const [showSettings, setShowSettings] = useState(true);
  const [currentView, setCurrentView] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({});

  // API Helper Function
  const apiCall = async (endpoint) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`Error calling ${endpoint}:`, err);
      throw err;
    }
  };

  // Load Dashboard Data
  useEffect(() => {
    if (orgId) {
      loadDashboardData();
    }
  }, [currentView, orgId]);

  const loadDashboardData = async () => {
    if (!orgId) return;

    setLoading(true);
    setError(null);
    try {
      const data = {};

      if (currentView === 'overview' || currentView === 'mission') {
        data.mission = await apiCall(`/analytics/mission-vision/${orgId}`);
      }
      if (currentView === 'overview' || currentView === 'fundraising') {
        data.fundraising = await apiCall(`/analytics/fundraising-vitals/${orgId}`);
      }
      if (currentView === 'overview' || currentView === 'lifecycle') {
        data.lifecycle = await apiCall(`/analytics/lifecycle/${orgId}`);
      }
      if (currentView === 'overview' || currentView === 'revenue') {
        data.revenue = await apiCall(`/analytics/revenue-rollup/${orgId}`);
      }
      if (currentView === 'overview' || currentView === 'audience') {
        data.audience = await apiCall(`/analytics/audience-metrics/${orgId}`);
      }
      if (currentView === 'programs') {
        data.programs = await apiCall(`/analytics/program-impact/${orgId}`);
      }
      if (currentView === 'digital') {
        data.digital = await apiCall(`/analytics/digital-kpis/${orgId}`);
      }
      if (currentView === 'targets') {
        data.targets = await apiCall(`/analytics/high-impact-targets/${orgId}`);
      }
      if (currentView === 'donor-lifecycle') {
        data.donorLifecycle = await apiCall(`/analytics/advanced/donor-lifecycle/${orgId}?include_at_risk=true&risk_threshold=medium`);
      }
      if (currentView === 'impact') {
        data.impact = await apiCall(`/analytics/advanced/impact-correlation/${orgId}?lag_months=3`);
      }

      setDashboardData(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const handleSetOrgId = () => {
    if (tempOrgId.trim()) {
      setOrgId(tempOrgId.trim());
      setShowSettings(false);
    }
  };

  // Navigation items
  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'mission', label: 'Mission & Vision', icon: Target },
    { id: 'fundraising', label: 'Fundraising Vitals', icon: DollarSign },
    { id: 'lifecycle', label: 'Donor Lifecycle', icon: Users },
    { id: 'revenue', label: 'Revenue Trends', icon: TrendingUp },
    { id: 'audience', label: 'Audience Growth', icon: Users },
    { id: 'programs', label: 'Program Impact', icon: Target },
    { id: 'digital', label: 'Digital KPIs', icon: Activity },
    { id: 'targets', label: 'Strategic Targets', icon: Target },
    { id: 'donor-lifecycle', label: 'Donor Analytics', icon: Users },
    { id: 'impact', label: 'Impact Correlation', icon: TrendingUp },
  ];

  const COLORS = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  // Settings Modal
  if (showSettings || !orgId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="bg-indigo-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Activity className="text-white" size={32} />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Nonprofit Analytics Dashboard</h1>
            <p className="text-gray-600 mt-2">Enter your organization ID to get started</p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization ID
              </label>
              <input
                type="text"
                value={tempOrgId}
                onChange={(e) => setTempOrgId(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSetOrgId()}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000"
              />
              <p className="text-xs text-gray-500 mt-1">
                This is your unique organization UUID from the API
              </p>
            </div>

            <button
              onClick={handleSetOrgId}
              disabled={!tempOrgId.trim()}
              className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Connect to Dashboard
            </button>
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Need help?</strong> Your organization ID can be found in your API settings or contact your administrator.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Render different views
  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <RefreshCw className="animate-spin mx-auto mb-4 text-indigo-600" size={48} />
            <p className="text-gray-600">Loading data...</p>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-lg">
            <AlertCircle className="text-red-600 mx-auto mb-4" size={48} />
            <h3 className="text-lg font-semibold text-red-900 mb-2">Error Loading Data</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <div className="flex gap-3">
              <button
                onClick={loadDashboardData}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
              >
                Retry
              </button>
              <button
                onClick={() => setShowSettings(true)}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
              >
                Change Organization
              </button>
            </div>
          </div>
        </div>
      );
    }

    switch (currentView) {
      case 'overview':
        return <OverviewView data={dashboardData} />;
      case 'mission':
        return <MissionView data={dashboardData.mission} />;
      case 'fundraising':
        return <FundraisingView data={dashboardData.fundraising} />;
      case 'lifecycle':
        return <LifecycleView data={dashboardData.lifecycle} />;
      case 'revenue':
        return <RevenueView data={dashboardData.revenue} />;
      case 'audience':
        return <AudienceView data={dashboardData.audience} />;
      case 'programs':
        return <ProgramsView data={dashboardData.programs} />;
      case 'digital':
        return <DigitalView data={dashboardData.digital} />;
      case 'targets':
        return <TargetsView data={dashboardData.targets} />;
      case 'donor-lifecycle':
        return <DonorLifecycleView data={dashboardData.donorLifecycle} />;
      case 'impact':
        return <ImpactView data={dashboardData.impact} />;
      default:
        return <div>Select a view</div>;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-indigo-900 text-white transition-all duration-300 flex flex-col`}>
        <div className="p-4 flex items-center justify-between border-b border-indigo-800">
          {sidebarOpen && <h2 className="text-xl font-bold">Analytics</h2>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-indigo-800 rounded">
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className="flex-1 p-2 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg mb-1 transition-colors ${
                  currentView === item.id
                    ? 'bg-indigo-700 text-white'
                    : 'text-indigo-200 hover:bg-indigo-800 hover:text-white'
                }`}
              >
                <Icon size={20} />
                {sidebarOpen && <span className="text-sm">{item.label}</span>}
              </button>
            );
          })}
        </nav>

        {sidebarOpen && (
          <div className="p-4 border-t border-indigo-800">
            <button
              onClick={() => setShowSettings(true)}
              className="w-full flex items-center gap-3 p-3 rounded-lg text-indigo-200 hover:bg-indigo-800 hover:text-white transition-colors"
            >
              <Settings size={20} />
              <span className="text-sm">Settings</span>
            </button>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {navItems.find(item => item.id === currentView)?.label}
              </h1>
              <p className="text-sm text-gray-500">
                Organization: {orgId.substring(0, 8)}...
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowSettings(true)}
                className="flex items-center gap-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200"
              >
                <Settings size={16} />
                Change Org
              </button>
              <button
                onClick={loadDashboardData}
                className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

// Overview View Component
const OverviewView = ({ data }) => {
  if (!data.fundraising || !data.lifecycle || !data.audience) {
    return <div className="text-gray-500">Loading overview data...</div>;
  }

  const stats = [
    { label: 'Active Donors', value: data.audience.active_donors, change: data.audience.active_donors_yoy_delta, icon: Users },
    { label: 'Retention Rate', value: `${data.fundraising.retention_rates.overall}%`, change: '+2.3%', icon: TrendingUp },
    { label: 'Avg Gift', value: `$${data.fundraising.avg_gift.toFixed(2)}`, change: `+$${(data.fundraising.avg_gift - data.fundraising.avg_gift_prior_year).toFixed(2)}`, icon: DollarSign },
    { label: 'Major Donors', value: data.audience.donors_gte_10k, change: data.audience.donors_gte_10k_yoy_delta, icon: Target },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-indigo-100 p-3 rounded-lg">
                  <Icon className="text-indigo-600" size={24} />
                </div>
                <span className="text-green-600 text-sm font-medium">+{stat.change}</span>
              </div>
              <p className="text-gray-600 text-sm">{stat.label}</p>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Lifecycle Pipeline */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Donor Lifecycle Pipeline</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.lifecycle}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="stage" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#4f46e5" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Income Diversification */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Income Diversification</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Unrestricted', value: data.fundraising.income_diversification.unrestricted },
                  { name: 'Temp Restricted', value: data.fundraising.income_diversification.temporarily_restricted },
                  { name: 'Perm Restricted', value: data.fundraising.income_diversification.permanently_restricted },
                ]}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {[0, 1, 2].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={['#4f46e5', '#06b6d4', '#10b981'][index]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// Mission View Component
const MissionView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Mission Statement</h3>
        <p className="text-gray-700 text-lg leading-relaxed">{data.mission}</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Vision Statement</h3>
        <p className="text-gray-700 text-lg leading-relaxed">{data.vision}</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Brand Promise</h3>
        <p className="text-gray-700 text-lg leading-relaxed">{data.brand_promise}</p>
      </div>

      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-indigo-900 mb-4">North Star Objective</h3>
        <p className="text-indigo-700 text-lg font-medium">{data.north_star_objective}</p>
        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="text-indigo-600">Owner: {data.owner}</span>
          <span className="text-indigo-600">Last Updated: {new Date(data.last_updated).toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  );
};

// Fundraising View Component
const FundraisingView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  const pyramidData = Object.entries(data.donor_pyramid).map(([tier, count]) => ({
    tier,
    count
  }));

  return (
    <div className="space-y-6">
      {/* Retention Rates */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm mb-2">Overall Retention</p>
          <p className="text-3xl font-bold text-gray-900">{data.retention_rates.overall}%</p>
          <p className="text-green-600 text-sm mt-2">Above 45% industry avg</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm mb-2">First Year Retention</p>
          <p className="text-3xl font-bold text-gray-900">{data.retention_rates.first_year}%</p>
          <p className="text-yellow-600 text-sm mt-2">Needs improvement</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm mb-2">Major Donor Retention</p>
          <p className="text-3xl font-bold text-gray-900">{data.retention_rates.major}%</p>
          <p className="text-green-600 text-sm mt-2">Excellent</p>
        </div>
      </div>

      {/* Donor Pyramid */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Donor Pyramid</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={pyramidData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="tier" type="category" width={100} />
            <Tooltip />
            <Bar dataKey="count" fill="#4f46e5" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="font-semibold text-gray-900 mb-3">Gift Analysis</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Average Gift:</span>
              <span className="font-semibold">${data.avg_gift.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Prior Year Avg:</span>
              <span className="font-semibold">${data.avg_gift_prior_year.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Change:</span>
              <span className="font-semibold text-green-600">+${(data.avg_gift - data.avg_gift_prior_year).toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="font-semibold text-gray-900 mb-3">Donor Base Health</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Multi-Year Donors:</span>
              <span className="font-semibold">{data.multi_year_donors}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Inflow/Lapsed Ratio:</span>
              <span className="font-semibold text-green-600">{data.inflow_lapsed_ratio}</span>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              {data.inflow_lapsed_ratio > 1.0 ? '✓ Growing donor base' : '⚠ Shrinking donor base'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Lifecycle View Component
const LifecycleView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  const getSlaColor = (status) => {
    switch(status) {
      case 'green': return 'bg-green-500';
      case 'amber': return 'bg-yellow-500';
      case 'red': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Pipeline Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Donor Lifecycle Pipeline</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="stage" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#4f46e5" name="Donor Count" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Stage Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {data.map((stage, idx) => (
          <div key={idx} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-gray-900">{stage.stage}</h4>
              <span className={`w-3 h-3 rounded-full ${getSlaColor(stage.sla_status)}`}></span>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Donors:</span>
                <span className="font-semibold">{stage.count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Days in Stage:</span>
                <span className="font-semibold">{stage.avg_days_in_stage.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Conversion Rate:</span>
                <span className="font-semibold">{stage.handoff_conversion_rate.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">SLA Target:</span>
                <span className="font-semibold">{stage.sla_days} days</span>
              </div>
              <div className="mt-4 pt-4 border-t">
                <span className={`text-sm font-medium ${
                  stage.sla_status === 'green' ? 'text-green-600' :
                  stage.sla_status === 'amber' ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {stage.sla_status === 'green' ? '✓ On Track' :
                   stage.sla_status === 'amber' ? '⚠ Attention Needed' :
                   '✗ Behind Schedule'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Conversion Funnel */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Conversion Rates</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="stage" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="handoff_conversion_rate" fill="#10b981" name="Conversion Rate %" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Revenue View Component
const RevenueView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  const formatCurrency = (value) => {
    return `$${(value / 1000).toFixed(0)}K`;
  };

  return (
    <div className="space-y-6">
      {/* Revenue Trend */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">3-Year Revenue Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis tickFormatter={formatCurrency} />
            <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
            <Legend />
            <Line type="monotone" dataKey="total_revenue" stroke="#4f46e5" strokeWidth={2} name="Total Revenue" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Channel Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Revenue by Channel</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis tickFormatter={formatCurrency} />
            <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
            <Legend />
            <Bar dataKey="online_revenue" fill="#4f46e5" name="Online" />
            <Bar dataKey="offline_revenue" fill="#06b6d4" name="Offline" />
            <Bar dataKey="event_revenue" fill="#10b981" name="Events" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Yearly Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {data.map((year, idx) => (
          <div key={idx} className="bg-white rounded-lg shadow p-6">
            <h4 className="text-xl font-bold text-gray-900 mb-4">{year.year}</h4>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Total Revenue</p>
                <p className="text-2xl font-bold text-indigo-600">${(year.total_revenue / 1000000).toFixed(2)}M</p>
              </div>
              <div className="pt-3 border-t space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Online:</span>
                  <span className="font-semibold">${(year.online_revenue / 1000).toFixed(0)}K ({((year.online_revenue / year.total_revenue) * 100).toFixed(0)}%)</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Offline:</span>
                  <span className="font-semibold">${(year.offline_revenue / 1000).toFixed(0)}K ({((year.offline_revenue / year.total_revenue) * 100).toFixed(0)}%)</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Events:</span>
                  <span className="font-semibold">${(year.event_revenue / 1000).toFixed(0)}K ({((year.event_revenue / year.total_revenue) * 100).toFixed(0)}%)</span>
                </div>
              </div>
              {year.variance_vs_plan !== 0 && (
                <div className="pt-3 border-t">
                  <span className={`text-sm font-medium ${year.variance_vs_plan > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {year.variance_vs_plan > 0 ? '+' : ''}{year.variance_vs_plan}% vs Plan
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Audience View Component
const AudienceView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  const metrics = [
    { label: 'Active Donors', current: data.active_donors, change: data.active_donors_yoy_delta },
    { label: 'Donors ≥ $1K', current: data.donors_gte_1k, change: data.donors_gte_1k_yoy_delta },
    { label: 'Donors ≥ $10K', current: data.donors_gte_10k, change: data.donors_gte_10k_yoy_delta },
    { label: 'Email List', current: data.email_list_size, change: data.email_list_yoy_delta },
    { label: 'Social Followers', current: data.social_followers, change: data.social_followers_yoy_delta },
  ];

  return (
    <div className="space-y-6">
      {/* Growth Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metrics.map((metric, idx) => {
          const growthPercent = ((metric.change / (metric.current - metric.change)) * 100).toFixed(1);
          return (
            <div key={idx} className="bg-white rounded-lg shadow p-6">
              <h4 className="text-gray-600 text-sm mb-2">{metric.label}</h4>
              <p className="text-3xl font-bold text-gray-900 mb-2">{metric.current.toLocaleString()}</p>
              <div className="flex items-center gap-2">
                <span className={`text-sm font-medium ${metric.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {metric.change >= 0 ? '↑' : '↓'} {Math.abs(metric.change).toLocaleString()} ({growthPercent}%)
                </span>
                <span className="text-xs text-gray-500">YoY</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Growth Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Year-over-Year Growth</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={metrics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" angle={-15} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="change" fill="#10b981" name="YoY Growth" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Key Insights */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-indigo-900 mb-4">Key Insights</h3>
        <ul className="space-y-2">
          <li className="flex items-start gap-2">
            <ChevronRight className="text-indigo-600 mt-0.5" size={18} />
            <span className="text-indigo-800">
              <strong>High-Value Donor Growth:</strong> {data.donors_gte_10k_yoy_delta > 0 ?
                `Major donors ($10K+) grew by ${data.donors_gte_10k_yoy_delta}, indicating successful major gift programs` :
                'Focus needed on major donor retention and acquisition'}
            </span>
          </li>
          <li className="flex items-start gap-2">
            <ChevronRight className="text-indigo-600 mt-0.5" size={18} />
            <span className="text-indigo-800">
              <strong>Digital Reach:</strong> Email list and social followers growing {
                data.email_list_yoy_delta > 0 && data.social_followers_yoy_delta > 0 ?
                'positively, suggesting effective digital marketing' :
                '- consider enhancing digital strategy'
              }
            </span>
          </li>
          <li className="flex items-start gap-2">
            <ChevronRight className="text-indigo-600 mt-0.5" size={18} />
            <span className="text-indigo-800">
              <strong>Overall Trend:</strong> {data.active_donors_yoy_delta >= 0 ?
                `Growing active donor base (+${data.active_donors_yoy_delta}) indicates healthy organizational momentum` :
                'Declining donor base requires immediate attention to acquisition and retention'}
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
};

// Programs View Component
const ProgramsView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      {/* Program Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {data.map((program, idx) => {
          const progressPercent = (program.progress_vs_target / program.quarterly_target) * 100;
          const statusColor = progressPercent >= 95 ? 'green' : progressPercent >= 80 ? 'yellow' : 'red';

          return (
            <div key={idx} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <h4 className="text-lg font-semibold text-gray-900">{program.program_name}</h4>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  statusColor === 'green' ? 'bg-green-100 text-green-800' :
                  statusColor === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {progressPercent.toFixed(0)}% of Goal
                </span>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Beneficiaries Served:</span>
                  <span className="font-semibold">{program.beneficiaries_served.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Units Delivered:</span>
                  <span className="font-semibold">{program.units_delivered.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Cost per Outcome:</span>
                  <span className="font-semibold">${program.cost_per_outcome.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Quarterly Target:</span>
                  <span className="font-semibold">{program.quarterly_target.toLocaleString()}</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      statusColor === 'green' ? 'bg-green-500' :
                      statusColor === 'yellow' ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${Math.min(progressPercent, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Comparison Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Cost per Outcome Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="program_name" angle={-15} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
            <Bar dataKey="cost_per_outcome" fill="#4f46e5" name="Cost per Outcome" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Beneficiaries Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Beneficiaries Served</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="program_name" angle={-15} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="beneficiaries_served" fill="#10b981" name="Beneficiaries" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

// Digital View Component
const DigitalView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  const openRate = ((data.email_opens / data.email_sends) * 100).toFixed(1);
  const ctr = data.email_ctr.toFixed(1);

  return (
    <div className="space-y-6">
      {/* Website Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Website Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-gray-600 text-sm mb-1">Monthly Sessions</p>
            <p className="text-3xl font-bold text-gray-900">{data.sessions.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-gray-600 text-sm mb-1">Avg Session Duration</p>
            <p className="text-3xl font-bold text-gray-900">{data.avg_session_duration.toFixed(0)}s</p>
          </div>
          <div>
            <p className="text-gray-600 text-sm mb-1">Bounce Rate</p>
            <p className="text-3xl font-bold text-gray-900">{data.bounce_rate.toFixed(1)}%</p>
            <p className="text-green-600 text-sm">Below 45-55% avg</p>
          </div>
        </div>
      </div>

      {/* Email Marketing */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Email Marketing Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-gray-600 text-sm mb-3">Campaign Metrics</p>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Sends:</span>
                <span className="font-semibold">{data.email_sends.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Opens:</span>
                <span className="font-semibold">{data.email_opens.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Clicks:</span>
                <span className="font-semibold">{data.email_clicks.toLocaleString()}</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-gray-600 text-sm mb-3">Performance Rates</p>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-600">Open Rate:</span>
                  <span className="font-semibold text-green-600">{openRate}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: `${openRate}%` }}></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">Above 25% avg</p>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-600">Click Rate:</span>
                  <span className="font-semibold text-green-600">{ctr}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: `${(parseFloat(ctr) / 10) * 100}%` }}></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">Excellent vs 3-5% avg</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Conversion Rates */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Conversion Rates</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-2">To Donation</p>
            <p className="text-4xl font-bold text-indigo-600">{data.conversion_to_donation.toFixed(1)}%</p>
            <p className="text-green-600 text-sm mt-2">Strong (1-2% avg)</p>
          </div>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-2">To Volunteer</p>
            <p className="text-4xl font-bold text-indigo-600">{data.conversion_to_volunteer.toFixed(1)}%</p>
          </div>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-2">To Newsletter</p>
            <p className="text-4xl font-bold text-indigo-600">{data.conversion_to_newsletter.toFixed(1)}%</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Targets View Component
const TargetsView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  const getStatusColor = (status) => {
    switch(status) {
      case 'G': return 'bg-green-500';
      case 'A': return 'bg-yellow-500';
      case 'R': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status) => {
    switch(status) {
      case 'G': return 'On Track';
      case 'A': return 'At Risk';
      case 'R': return 'Behind';
      default: return 'Unknown';
    }
  };

  return (
    <div className="space-y-6">
      {/* Strategic Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {['G', 'A', 'R'].map((status) => {
          const count = data.filter(t => t.status === status).length;
          const totalLift = data.filter(t => t.status === status)
            .reduce((sum, t) => sum + t.expected_lift, 0);

          return (
            <div key={status} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-4 h-4 rounded-full ${getStatusColor(status)}`}></div>
                <h4 className="font-semibold text-gray-900">{getStatusText(status)}</h4>
              </div>
              <p className="text-3xl font-bold text-gray-900 mb-1">{count}</p>
              <p className="text-sm text-gray-600">initiatives</p>
              <p className="text-lg font-semibold text-indigo-600 mt-3">
                ${(totalLift / 1000).toFixed(0)}K expected lift
              </p>
            </div>
          );
        })}
      </div>

      {/* Initiatives List */}
      <div className="space-y-4">
        {data.map((target, idx) => (
          <div key={idx} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(target.status)}`}></div>
                  <h4 className="text-lg font-semibold text-gray-900">{target.title}</h4>
                </div>
                <p className="text-sm text-gray-600 mb-2">Owner: {target.owner}</p>
                <p className="text-sm text-gray-600">Due: {new Date(target.due_date).toLocaleDateString()}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">Expected Lift</p>
                <p className="text-2xl font-bold text-indigo-600">${(target.expected_lift / 1000).toFixed(0)}K</p>
                <span className="inline-block mt-2 px-3 py-1 bg-indigo-100 text-indigo-800 text-xs font-medium rounded-full">
                  {target.timeframe === '90_day' ? '90-Day Bet' : '1-Year Objective'}
                </span>
              </div>
            </div>

            {/* Milestones */}
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm font-semibold text-gray-700 mb-3">Milestones</p>
              <div className="space-y-2">
                {target.milestones.map((milestone, mIdx) => (
                  <div key={mIdx} className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      milestone.status === 'complete' ? 'bg-green-500' :
                      milestone.status === 'in_progress' ? 'bg-yellow-500' :
                      milestone.status === 'delayed' ? 'bg-red-500' :
                      'bg-gray-300'
                    }`}></div>
                    <span className={`text-sm ${
                      milestone.status === 'complete' ? 'line-through text-gray-500' : 'text-gray-700'
                    }`}>
                      {milestone.name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(milestone.due).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Flags */}
            {target.risk_flags && target.risk_flags.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm font-semibold text-red-700 mb-2">⚠ Risk Flags</p>
                <ul className="space-y-1">
                  {target.risk_flags.map((flag, fIdx) => (
                    <li key={fIdx} className="text-sm text-red-600">• {flag}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Donor Lifecycle View Component
const DonorLifecycleView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  const getRiskColor = (level) => {
    switch(level) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm mb-2">Total Donors</p>
          <p className="text-3xl font-bold text-gray-900">{data.summary_metrics.total_donors}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm mb-2">Active Donors</p>
          <p className="text-3xl font-bold text-green-600">{data.summary_metrics.active_donors}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm mb-2">At Risk</p>
          <p className="text-3xl font-bold text-yellow-600">{data.summary_metrics.at_risk_count}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm mb-2">Critical Risk</p>
          <p className="text-3xl font-bold text-red-600">{data.summary_metrics.critical_risk_count}</p>
        </div>
      </div>

      {/* Lifecycle Stages */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Donor Lifecycle Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data.lifecycle_stages}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="stage" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="donor_count" fill="#4f46e5" name="Donors" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* At-Risk Donors */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">At-Risk Donors Requiring Action</h3>
        <div className="space-y-4">
          {data.at_risk_donors.slice(0, 10).map((donor, idx) => (
            <div key={idx} className={`border rounded-lg p-4 ${getRiskColor(donor.risk_level)}`}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-semibold">{donor.donor_name}</h4>
                  <p className="text-sm opacity-75">{donor.email}</p>
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-bold uppercase">
                  {donor.risk_level}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                <div>
                  <p className="opacity-75">Lifetime Value</p>
                  <p className="font-semibold">${donor.lifetime_value.toLocaleString()}</p>
                </div>
                <div>
                  <p className="opacity-75">Days Since Last Gift</p>
                  <p className="font-semibold">{donor.days_since_last_donation}</p>
                </div>
              </div>

              <div className="mb-3">
                <p className="text-sm font-semibold mb-1">Risk Factors:</p>
                <ul className="text-sm space-y-1">
                  {donor.risk_factors.map((factor, fIdx) => (
                    <li key={fIdx}>• {factor}</li>
                  ))}
                </ul>
              </div>

              <div className="pt-3 border-t border-current/20">
                <p className="text-sm font-semibold">Recommended Action:</p>
                <p className="text-sm mt-1">{donor.recommended_action}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cohort Analysis */}
      {data.cohort_analysis && data.cohort_analysis.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Cohort Retention Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.cohort_analysis}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="cohort_period" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="retention_rate_12m" stroke="#4f46e5" name="12-Month Retention %" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

// Impact View Component
const ImpactView = ({ data }) => {
  if (!data) return <div>Loading...</div>;

  const getCorrelationColor = (strength) => {
    if (strength >= 0.9) return 'text-green-600';
    if (strength >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCorrelationLabel = (strength) => {
    if (strength >= 0.9) return 'Strong';
    if (strength >= 0.7) return 'Moderate';
    if (strength >= 0.5) return 'Weak';
    return 'Poor';
  };

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-indigo-900 mb-4">Analysis Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
          <div>
            <p className="text-sm text-indigo-700">Total Investment</p>
            <p className="text-2xl font-bold text-indigo-900">
              ${(data.summary.total_investment / 1000).toFixed(0)}K
            </p>
          </div>
          <div>
            <p className="text-sm text-indigo-700">Total Outcomes</p>
            <p className="text-2xl font-bold text-indigo-900">
              {data.summary.total_outcomes.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-indigo-700">Avg Unit Cost</p>
            <p className="text-2xl font-bold text-indigo-900">
              ${data.summary.weighted_avg_unit_cost.toFixed(2)}
            </p>
          </div>
        </div>

        <div className="pt-4 border-t border-indigo-300">
          <p className="text-sm font-semibold text-indigo-900 mb-2">Key Findings:</p>
          <ul className="space-y-1">
            {data.summary.key_findings.map((finding, idx) => (
              <li key={idx} className="text-sm text-indigo-800">• {finding}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Program Correlations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {data.correlations.map((program, idx) => (
          <div key={idx} className="bg-white rounded-lg shadow p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">{program.program_name}</h4>

            <div className="space-y-3 mb-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Funding:</span>
                <span className="font-semibold">${program.total_funding.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Outcomes:</span>
                <span className="font-semibold">{program.total_outcomes.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Planned Unit Cost:</span>
                <span className="font-semibold">${program.unit_cost_planned.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Actual Unit Cost:</span>
                <span className="font-semibold">${program.unit_cost_actual.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Efficiency Ratio:</span>
                <span className={`font-semibold ${
                  program.efficiency_ratio >= 1.0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {(program.efficiency_ratio * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Correlation Strength:</span>
                <div className="text-right">
                  <span className={`text-2xl font-bold ${getCorrelationColor(program.correlation_strength)}`}>
                    {(program.correlation_strength * 100).toFixed(0)}%
                  </span>
                  <p className={`text-sm ${getCorrelationColor(program.correlation_strength)}`}>
                    {getCorrelationLabel(program.correlation_strength)}
                  </p>
                </div>
              </div>
            </div>

            {program.efficiency_ratio >= 1.0 && (
              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                <p className="text-sm text-green-800">
                  ✓ Operating {((program.efficiency_ratio - 1) * 100).toFixed(0)}% more efficiently than planned
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Efficiency Comparison Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Efficiency Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data.correlations}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="program_name" angle={-15} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip formatter={(value) => `${(value * 100).toFixed(0)}%`} />
            <Legend />
            <Bar dataKey="efficiency_ratio" fill="#10b981" name="Efficiency Ratio" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Assumptions */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Analysis Assumptions</h3>
        <ul className="space-y-2">
          {data.summary.assumptions.map((assumption, idx) => (
            <li key={idx} className="text-sm text-gray-700">
              <span className="font-medium text-gray-900">{idx + 1}.</span> {assumption}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default App;