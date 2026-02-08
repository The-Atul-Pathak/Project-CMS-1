--
-- PostgreSQL database dump
--

\restrict CcG9HMSlhnvbSq2PpFcKvyfLRH4qvYsqTpVEgPmqUs7AUbddUSUv2JeFJC64gXi

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.0

-- Started on 2026-02-08 06:26:45 IST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 274 (class 1259 OID 17236)
-- Name: attendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance (
    id integer NOT NULL,
    company_id integer NOT NULL,
    user_id integer NOT NULL,
    date date NOT NULL,
    status character varying(20) NOT NULL,
    marked_by integer NOT NULL,
    marked_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    remarks text,
    CONSTRAINT attendance_status_check CHECK (((status)::text = ANY ((ARRAY['Present'::character varying, 'Absent'::character varying, 'Leave'::character varying])::text[])))
);


ALTER TABLE public.attendance OWNER TO postgres;

--
-- TOC entry 273 (class 1259 OID 17235)
-- Name: attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_id_seq OWNER TO postgres;

--
-- TOC entry 4245 (class 0 OID 0)
-- Dependencies: 273
-- Name: attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendance_id_seq OWNED BY public.attendance.id;


--
-- TOC entry 252 (class 1259 OID 16671)
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id integer NOT NULL,
    action character varying(100) NOT NULL,
    performed_by character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 16670)
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- TOC entry 4246 (class 0 OID 0)
-- Dependencies: 251
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- TOC entry 222 (class 1259 OID 16412)
-- Name: companies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    company_name character varying(150) NOT NULL,
    legal_name character varying(200),
    domain character varying(150),
    industry character varying(100),
    employee_size_range character varying(50),
    status character varying(20) DEFAULT 'trial'::character varying,
    onboarding_status character varying(50) DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.companies OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16411)
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO postgres;

--
-- TOC entry 4247 (class 0 OID 0)
-- Dependencies: 221
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- TOC entry 266 (class 1259 OID 17141)
-- Name: company_activity_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_activity_logs (
    id integer NOT NULL,
    company_id integer NOT NULL,
    user_id integer,
    action character varying(150) NOT NULL,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.company_activity_logs OWNER TO postgres;

--
-- TOC entry 265 (class 1259 OID 17140)
-- Name: company_activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_activity_logs_id_seq OWNER TO postgres;

--
-- TOC entry 4248 (class 0 OID 0)
-- Dependencies: 265
-- Name: company_activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_activity_logs_id_seq OWNED BY public.company_activity_logs.id;


--
-- TOC entry 224 (class 1259 OID 16427)
-- Name: company_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_contacts (
    id integer NOT NULL,
    company_id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(150),
    phone character varying(20),
    designation character varying(100),
    is_primary boolean DEFAULT false
);


ALTER TABLE public.company_contacts OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16426)
-- Name: company_contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_contacts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_contacts_id_seq OWNER TO postgres;

--
-- TOC entry 4249 (class 0 OID 0)
-- Dependencies: 223
-- Name: company_contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_contacts_id_seq OWNED BY public.company_contacts.id;


--
-- TOC entry 232 (class 1259 OID 16491)
-- Name: company_features; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_features (
    id integer NOT NULL,
    company_id integer NOT NULL,
    feature_id integer NOT NULL,
    enabled boolean DEFAULT true,
    enabled_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.company_features OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16490)
-- Name: company_features_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_features_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_features_id_seq OWNER TO postgres;

--
-- TOC entry 4250 (class 0 OID 0)
-- Dependencies: 231
-- Name: company_features_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_features_id_seq OWNED BY public.company_features.id;


--
-- TOC entry 248 (class 1259 OID 16637)
-- Name: company_health_scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_health_scores (
    id integer NOT NULL,
    company_id integer NOT NULL,
    score integer,
    last_calculated_at timestamp without time zone,
    CONSTRAINT company_health_scores_score_check CHECK (((score >= 0) AND (score <= 100)))
);


ALTER TABLE public.company_health_scores OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 16636)
-- Name: company_health_scores_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_health_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_health_scores_id_seq OWNER TO postgres;

--
-- TOC entry 4251 (class 0 OID 0)
-- Dependencies: 247
-- Name: company_health_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_health_scores_id_seq OWNED BY public.company_health_scores.id;


--
-- TOC entry 238 (class 1259 OID 16550)
-- Name: company_onboarding_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_onboarding_logs (
    id integer NOT NULL,
    company_id integer NOT NULL,
    step character varying(100) NOT NULL,
    status character varying(30) NOT NULL,
    completed_at timestamp without time zone
);


ALTER TABLE public.company_onboarding_logs OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 16549)
-- Name: company_onboarding_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_onboarding_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_onboarding_logs_id_seq OWNER TO postgres;

--
-- TOC entry 4252 (class 0 OID 0)
-- Dependencies: 237
-- Name: company_onboarding_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_onboarding_logs_id_seq OWNED BY public.company_onboarding_logs.id;


--
-- TOC entry 234 (class 1259 OID 16515)
-- Name: company_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_settings (
    id integer NOT NULL,
    company_id integer NOT NULL,
    setting_key character varying(100) NOT NULL,
    setting_value jsonb NOT NULL
);


ALTER TABLE public.company_settings OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16514)
-- Name: company_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_settings_id_seq OWNER TO postgres;

--
-- TOC entry 4253 (class 0 OID 0)
-- Dependencies: 233
-- Name: company_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_settings_id_seq OWNED BY public.company_settings.id;


--
-- TOC entry 228 (class 1259 OID 16453)
-- Name: company_subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_subscriptions (
    id integer NOT NULL,
    company_id integer NOT NULL,
    plan_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying,
    auto_renew boolean DEFAULT true
);


ALTER TABLE public.company_subscriptions OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16452)
-- Name: company_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_subscriptions_id_seq OWNER TO postgres;

--
-- TOC entry 4254 (class 0 OID 0)
-- Dependencies: 227
-- Name: company_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_subscriptions_id_seq OWNED BY public.company_subscriptions.id;


--
-- TOC entry 242 (class 1259 OID 16579)
-- Name: company_usage_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_usage_metrics (
    id integer NOT NULL,
    company_id integer NOT NULL,
    metric_date date NOT NULL,
    active_users integer DEFAULT 0,
    api_requests integer DEFAULT 0,
    storage_used_mb integer DEFAULT 0
);


ALTER TABLE public.company_usage_metrics OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 16578)
-- Name: company_usage_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_usage_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_usage_metrics_id_seq OWNER TO postgres;

--
-- TOC entry 4255 (class 0 OID 0)
-- Dependencies: 241
-- Name: company_usage_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_usage_metrics_id_seq OWNED BY public.company_usage_metrics.id;


--
-- TOC entry 270 (class 1259 OID 17188)
-- Name: feature_bundle_pages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_bundle_pages (
    id integer NOT NULL,
    feature_id integer NOT NULL,
    page_code character varying(50) NOT NULL,
    page_name character varying(100) NOT NULL,
    route character varying(150) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.feature_bundle_pages OWNER TO postgres;

--
-- TOC entry 269 (class 1259 OID 17187)
-- Name: feature_bundle_pages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_bundle_pages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feature_bundle_pages_id_seq OWNER TO postgres;

--
-- TOC entry 4256 (class 0 OID 0)
-- Dependencies: 269
-- Name: feature_bundle_pages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_bundle_pages_id_seq OWNED BY public.feature_bundle_pages.id;


--
-- TOC entry 244 (class 1259 OID 16599)
-- Name: feature_usage_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feature_usage_metrics (
    id integer NOT NULL,
    company_id integer NOT NULL,
    feature_id integer NOT NULL,
    metric_date date NOT NULL,
    usage_count integer DEFAULT 0
);


ALTER TABLE public.feature_usage_metrics OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 16598)
-- Name: feature_usage_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feature_usage_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feature_usage_metrics_id_seq OWNER TO postgres;

--
-- TOC entry 4257 (class 0 OID 0)
-- Dependencies: 243
-- Name: feature_usage_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feature_usage_metrics_id_seq OWNED BY public.feature_usage_metrics.id;


--
-- TOC entry 230 (class 1259 OID 16477)
-- Name: features; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.features (
    id integer NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    description text
);


ALTER TABLE public.features OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16476)
-- Name: features_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.features_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.features_id_seq OWNER TO postgres;

--
-- TOC entry 4258 (class 0 OID 0)
-- Dependencies: 229
-- Name: features_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.features_id_seq OWNED BY public.features.id;


--
-- TOC entry 284 (class 1259 OID 17453)
-- Name: lead_interactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lead_interactions (
    id integer NOT NULL,
    lead_id integer NOT NULL,
    interaction_type character varying(50) NOT NULL,
    description text NOT NULL,
    logged_by_employee_id integer NOT NULL,
    interaction_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.lead_interactions OWNER TO postgres;

--
-- TOC entry 283 (class 1259 OID 17452)
-- Name: lead_interactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lead_interactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lead_interactions_id_seq OWNER TO postgres;

--
-- TOC entry 4259 (class 0 OID 0)
-- Dependencies: 283
-- Name: lead_interactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lead_interactions_id_seq OWNED BY public.lead_interactions.id;


--
-- TOC entry 282 (class 1259 OID 17406)
-- Name: leads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.leads (
    id integer NOT NULL,
    client_name character varying(255) NOT NULL,
    contact_email character varying(255),
    contact_phone character varying(50),
    status character varying(50) DEFAULT 'New'::character varying NOT NULL,
    source character varying(255),
    notes text,
    assigned_employee_id integer NOT NULL,
    created_by_user_id integer NOT NULL,
    next_follow_up_date date,
    last_interaction_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    project_created boolean DEFAULT false,
    company_id integer NOT NULL
);


ALTER TABLE public.leads OWNER TO postgres;

--
-- TOC entry 281 (class 1259 OID 17405)
-- Name: leads_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.leads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.leads_id_seq OWNER TO postgres;

--
-- TOC entry 4260 (class 0 OID 0)
-- Dependencies: 281
-- Name: leads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.leads_id_seq OWNED BY public.leads.id;


--
-- TOC entry 276 (class 1259 OID 17255)
-- Name: leave_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.leave_requests (
    id integer NOT NULL,
    company_id integer NOT NULL,
    user_id integer NOT NULL,
    leave_type character varying(50) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    total_days numeric(4,1) NOT NULL,
    reason text,
    status character varying(20) DEFAULT 'Pending'::character varying NOT NULL,
    applied_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    reviewed_by integer,
    reviewed_at timestamp without time zone,
    review_notes text,
    CONSTRAINT chk_leave_status CHECK (((status)::text = ANY ((ARRAY['Pending'::character varying, 'Approved'::character varying, 'Rejected'::character varying, 'Cancelled'::character varying])::text[])))
);


ALTER TABLE public.leave_requests OWNER TO postgres;

--
-- TOC entry 275 (class 1259 OID 17254)
-- Name: leave_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.leave_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.leave_requests_id_seq OWNER TO postgres;

--
-- TOC entry 4261 (class 0 OID 0)
-- Dependencies: 275
-- Name: leave_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.leave_requests_id_seq OWNED BY public.leave_requests.id;


--
-- TOC entry 260 (class 1259 OID 17084)
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    code character varying(100) NOT NULL,
    description text
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- TOC entry 259 (class 1259 OID 17083)
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO postgres;

--
-- TOC entry 4262 (class 0 OID 0)
-- Dependencies: 259
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- TOC entry 226 (class 1259 OID 16443)
-- Name: plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plans (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    price_monthly numeric(10,2),
    price_yearly numeric(10,2),
    max_employees integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.plans OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16442)
-- Name: plans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plans_id_seq OWNER TO postgres;

--
-- TOC entry 4263 (class 0 OID 0)
-- Dependencies: 225
-- Name: plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.plans_id_seq OWNED BY public.plans.id;


--
-- TOC entry 240 (class 1259 OID 16566)
-- Name: platform_activity_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.platform_activity_logs (
    id integer NOT NULL,
    actor_type character varying(20) NOT NULL,
    actor_id integer,
    action character varying(150) NOT NULL,
    target_type character varying(50),
    target_id integer,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.platform_activity_logs OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16565)
-- Name: platform_activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.platform_activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.platform_activity_logs_id_seq OWNER TO postgres;

--
-- TOC entry 4264 (class 0 OID 0)
-- Dependencies: 239
-- Name: platform_activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.platform_activity_logs_id_seq OWNED BY public.platform_activity_logs.id;


--
-- TOC entry 220 (class 1259 OID 16393)
-- Name: platform_admins; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.platform_admins (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    password_hash text NOT NULL,
    role character varying(30) NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying,
    last_login_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT platform_admins_role_check CHECK (((role)::text = ANY ((ARRAY['SUPER_ADMIN'::character varying, 'SUPPORT'::character varying])::text[])))
);


ALTER TABLE public.platform_admins OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16392)
-- Name: platform_admins_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.platform_admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.platform_admins_id_seq OWNER TO postgres;

--
-- TOC entry 4265 (class 0 OID 0)
-- Dependencies: 219
-- Name: platform_admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.platform_admins_id_seq OWNED BY public.platform_admins.id;


--
-- TOC entry 246 (class 1259 OID 16623)
-- Name: platform_revenue_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.platform_revenue_metrics (
    id integer NOT NULL,
    metric_date date NOT NULL,
    total_revenue numeric(12,2) DEFAULT 0,
    active_subscriptions integer DEFAULT 0,
    churn_rate numeric(5,2) DEFAULT 0
);


ALTER TABLE public.platform_revenue_metrics OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 16622)
-- Name: platform_revenue_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.platform_revenue_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.platform_revenue_metrics_id_seq OWNER TO postgres;

--
-- TOC entry 4266 (class 0 OID 0)
-- Dependencies: 245
-- Name: platform_revenue_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.platform_revenue_metrics_id_seq OWNED BY public.platform_revenue_metrics.id;


--
-- TOC entry 250 (class 1259 OID 16654)
-- Name: platform_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.platform_sessions (
    id integer NOT NULL,
    admin_id integer NOT NULL,
    ip_address character varying(50),
    user_agent text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp without time zone
);


ALTER TABLE public.platform_sessions OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 16653)
-- Name: platform_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.platform_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.platform_sessions_id_seq OWNER TO postgres;

--
-- TOC entry 4267 (class 0 OID 0)
-- Dependencies: 249
-- Name: platform_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.platform_sessions_id_seq OWNED BY public.platform_sessions.id;


--
-- TOC entry 236 (class 1259 OID 16535)
-- Name: platform_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.platform_settings (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    value jsonb NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.platform_settings OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 16534)
-- Name: platform_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.platform_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.platform_settings_id_seq OWNER TO postgres;

--
-- TOC entry 4268 (class 0 OID 0)
-- Dependencies: 235
-- Name: platform_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.platform_settings_id_seq OWNED BY public.platform_settings.id;


--
-- TOC entry 288 (class 1259 OID 17518)
-- Name: project_planning; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_planning (
    id integer NOT NULL,
    project_id integer NOT NULL,
    company_id integer NOT NULL,
    planned_start_date date NOT NULL,
    planned_end_date date NOT NULL,
    description text NOT NULL,
    scope text,
    milestones jsonb,
    deliverables jsonb,
    estimated_budget numeric(12,2),
    priority character varying(20),
    client_requirements text,
    risk_notes text,
    assumptions text,
    dependencies text,
    client_review_checkpoints jsonb,
    internal_notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.project_planning OWNER TO postgres;

--
-- TOC entry 287 (class 1259 OID 17517)
-- Name: project_planning_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_planning_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_planning_id_seq OWNER TO postgres;

--
-- TOC entry 4269 (class 0 OID 0)
-- Dependencies: 287
-- Name: project_planning_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_planning_id_seq OWNED BY public.project_planning.id;


--
-- TOC entry 294 (class 1259 OID 17619)
-- Name: project_status_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_status_logs (
    id integer NOT NULL,
    project_id integer NOT NULL,
    company_id integer NOT NULL,
    old_status character varying(30),
    new_status character varying(30),
    changed_by integer NOT NULL,
    change_reason text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.project_status_logs OWNER TO postgres;

--
-- TOC entry 293 (class 1259 OID 17618)
-- Name: project_status_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_status_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_status_logs_id_seq OWNER TO postgres;

--
-- TOC entry 4270 (class 0 OID 0)
-- Dependencies: 293
-- Name: project_status_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_status_logs_id_seq OWNED BY public.project_status_logs.id;


--
-- TOC entry 290 (class 1259 OID 17547)
-- Name: project_tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_tasks (
    id integer NOT NULL,
    project_id integer NOT NULL,
    company_id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    assigned_to integer,
    created_by integer NOT NULL,
    start_date date,
    due_date date,
    estimated_effort_hours integer,
    cost_impact numeric(12,2),
    priority character varying(20),
    status character varying(30) DEFAULT 'Pending Approval'::character varying NOT NULL,
    dependency_task_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.project_tasks OWNER TO postgres;

--
-- TOC entry 289 (class 1259 OID 17546)
-- Name: project_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_tasks_id_seq OWNER TO postgres;

--
-- TOC entry 4271 (class 0 OID 0)
-- Dependencies: 289
-- Name: project_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_tasks_id_seq OWNED BY public.project_tasks.id;


--
-- TOC entry 286 (class 1259 OID 17481)
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    company_id integer NOT NULL,
    lead_id integer NOT NULL,
    project_name character varying(255) NOT NULL,
    assigned_team_id integer,
    status character varying(50) DEFAULT 'Unassigned'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.projects OWNER TO postgres;

--
-- TOC entry 285 (class 1259 OID 17480)
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.projects_id_seq OWNER TO postgres;

--
-- TOC entry 4272 (class 0 OID 0)
-- Dependencies: 285
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- TOC entry 262 (class 1259 OID 17097)
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    id integer NOT NULL,
    role_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- TOC entry 261 (class 1259 OID 17096)
-- Name: role_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.role_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.role_permissions_id_seq OWNER TO postgres;

--
-- TOC entry 4273 (class 0 OID 0)
-- Dependencies: 261
-- Name: role_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.role_permissions_id_seq OWNED BY public.role_permissions.id;


--
-- TOC entry 258 (class 1259 OID 17064)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    company_id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 268 (class 1259 OID 17166)
-- Name: roles_features; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles_features (
    id integer NOT NULL,
    role_id integer NOT NULL,
    feature_id integer NOT NULL
);


ALTER TABLE public.roles_features OWNER TO postgres;

--
-- TOC entry 267 (class 1259 OID 17165)
-- Name: roles_features_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_features_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_features_id_seq OWNER TO postgres;

--
-- TOC entry 4274 (class 0 OID 0)
-- Dependencies: 267
-- Name: roles_features_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_features_id_seq OWNED BY public.roles_features.id;


--
-- TOC entry 257 (class 1259 OID 17063)
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- TOC entry 4275 (class 0 OID 0)
-- Dependencies: 257
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- TOC entry 292 (class 1259 OID 17590)
-- Name: task_updates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_updates (
    id integer NOT NULL,
    task_id integer NOT NULL,
    company_id integer NOT NULL,
    updated_by integer NOT NULL,
    update_type character varying(30),
    old_status character varying(30),
    new_status character varying(30),
    note text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.task_updates OWNER TO postgres;

--
-- TOC entry 291 (class 1259 OID 17589)
-- Name: task_updates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_updates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.task_updates_id_seq OWNER TO postgres;

--
-- TOC entry 4276 (class 0 OID 0)
-- Dependencies: 291
-- Name: task_updates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.task_updates_id_seq OWNED BY public.task_updates.id;


--
-- TOC entry 280 (class 1259 OID 17320)
-- Name: team_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.team_members (
    id integer NOT NULL,
    team_id integer NOT NULL,
    user_id integer NOT NULL,
    added_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.team_members OWNER TO postgres;

--
-- TOC entry 279 (class 1259 OID 17319)
-- Name: team_members_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.team_members_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.team_members_id_seq OWNER TO postgres;

--
-- TOC entry 4277 (class 0 OID 0)
-- Dependencies: 279
-- Name: team_members_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.team_members_id_seq OWNED BY public.team_members.id;


--
-- TOC entry 278 (class 1259 OID 17292)
-- Name: teams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teams (
    id integer NOT NULL,
    company_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    manager_id integer,
    status character varying(20) DEFAULT 'Active'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.teams OWNER TO postgres;

--
-- TOC entry 277 (class 1259 OID 17291)
-- Name: teams_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teams_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teams_id_seq OWNER TO postgres;

--
-- TOC entry 4278 (class 0 OID 0)
-- Dependencies: 277
-- Name: teams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teams_id_seq OWNED BY public.teams.id;


--
-- TOC entry 272 (class 1259 OID 17210)
-- Name: user_profile_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_profile_data (
    id integer NOT NULL,
    user_id integer NOT NULL,
    company_id integer NOT NULL,
    phone character varying(20),
    alternate_phone character varying(20),
    address_line_1 text,
    address_line_2 text,
    city character varying(100),
    state character varying(100),
    postal_code character varying(20),
    country character varying(100),
    emergency_contact_name character varying(150),
    emergency_contact_phone character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_profile_data OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 17209)
-- Name: user_profile_data_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_profile_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_profile_data_id_seq OWNER TO postgres;

--
-- TOC entry 4279 (class 0 OID 0)
-- Dependencies: 271
-- Name: user_profile_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_profile_data_id_seq OWNED BY public.user_profile_data.id;


--
-- TOC entry 264 (class 1259 OID 17119)
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- TOC entry 263 (class 1259 OID 17118)
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_roles_id_seq OWNER TO postgres;

--
-- TOC entry 4280 (class 0 OID 0)
-- Dependencies: 263
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- TOC entry 256 (class 1259 OID 17040)
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    company_id integer NOT NULL,
    ip_address character varying(50),
    user_agent text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp without time zone NOT NULL
);


ALTER TABLE public.user_sessions OWNER TO postgres;

--
-- TOC entry 255 (class 1259 OID 17039)
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_sessions_id_seq OWNER TO postgres;

--
-- TOC entry 4281 (class 0 OID 0)
-- Dependencies: 255
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;


--
-- TOC entry 254 (class 1259 OID 17017)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    company_id integer NOT NULL,
    emp_id character varying(50) NOT NULL,
    name character varying(150) NOT NULL,
    email character varying(150),
    password_hash text NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_company_admin boolean DEFAULT false
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 17016)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4282 (class 0 OID 0)
-- Dependencies: 253
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 3880 (class 2604 OID 17239)
-- Name: attendance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance ALTER COLUMN id SET DEFAULT nextval('public.attendance_id_seq'::regclass);


--
-- TOC entry 3859 (class 2604 OID 16674)
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- TOC entry 3824 (class 2604 OID 16415)
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- TOC entry 3872 (class 2604 OID 17144)
-- Name: company_activity_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_activity_logs ALTER COLUMN id SET DEFAULT nextval('public.company_activity_logs_id_seq'::regclass);


--
-- TOC entry 3829 (class 2604 OID 16430)
-- Name: company_contacts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_contacts ALTER COLUMN id SET DEFAULT nextval('public.company_contacts_id_seq'::regclass);


--
-- TOC entry 3837 (class 2604 OID 16494)
-- Name: company_features id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_features ALTER COLUMN id SET DEFAULT nextval('public.company_features_id_seq'::regclass);


--
-- TOC entry 3856 (class 2604 OID 16640)
-- Name: company_health_scores id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_health_scores ALTER COLUMN id SET DEFAULT nextval('public.company_health_scores_id_seq'::regclass);


--
-- TOC entry 3843 (class 2604 OID 16553)
-- Name: company_onboarding_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_onboarding_logs ALTER COLUMN id SET DEFAULT nextval('public.company_onboarding_logs_id_seq'::regclass);


--
-- TOC entry 3840 (class 2604 OID 16518)
-- Name: company_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_settings ALTER COLUMN id SET DEFAULT nextval('public.company_settings_id_seq'::regclass);


--
-- TOC entry 3833 (class 2604 OID 16456)
-- Name: company_subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.company_subscriptions_id_seq'::regclass);


--
-- TOC entry 3846 (class 2604 OID 16582)
-- Name: company_usage_metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_usage_metrics ALTER COLUMN id SET DEFAULT nextval('public.company_usage_metrics_id_seq'::regclass);


--
-- TOC entry 3875 (class 2604 OID 17191)
-- Name: feature_bundle_pages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_bundle_pages ALTER COLUMN id SET DEFAULT nextval('public.feature_bundle_pages_id_seq'::regclass);


--
-- TOC entry 3850 (class 2604 OID 16602)
-- Name: feature_usage_metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_usage_metrics ALTER COLUMN id SET DEFAULT nextval('public.feature_usage_metrics_id_seq'::regclass);


--
-- TOC entry 3836 (class 2604 OID 16480)
-- Name: features id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.features ALTER COLUMN id SET DEFAULT nextval('public.features_id_seq'::regclass);


--
-- TOC entry 3895 (class 2604 OID 17456)
-- Name: lead_interactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lead_interactions ALTER COLUMN id SET DEFAULT nextval('public.lead_interactions_id_seq'::regclass);


--
-- TOC entry 3890 (class 2604 OID 17409)
-- Name: leads id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads ALTER COLUMN id SET DEFAULT nextval('public.leads_id_seq'::regclass);


--
-- TOC entry 3882 (class 2604 OID 17258)
-- Name: leave_requests id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leave_requests ALTER COLUMN id SET DEFAULT nextval('public.leave_requests_id_seq'::regclass);


--
-- TOC entry 3869 (class 2604 OID 17087)
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- TOC entry 3831 (class 2604 OID 16446)
-- Name: plans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plans ALTER COLUMN id SET DEFAULT nextval('public.plans_id_seq'::regclass);


--
-- TOC entry 3844 (class 2604 OID 16569)
-- Name: platform_activity_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_activity_logs ALTER COLUMN id SET DEFAULT nextval('public.platform_activity_logs_id_seq'::regclass);


--
-- TOC entry 3821 (class 2604 OID 16396)
-- Name: platform_admins id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_admins ALTER COLUMN id SET DEFAULT nextval('public.platform_admins_id_seq'::regclass);


--
-- TOC entry 3852 (class 2604 OID 16626)
-- Name: platform_revenue_metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_revenue_metrics ALTER COLUMN id SET DEFAULT nextval('public.platform_revenue_metrics_id_seq'::regclass);


--
-- TOC entry 3857 (class 2604 OID 16657)
-- Name: platform_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_sessions ALTER COLUMN id SET DEFAULT nextval('public.platform_sessions_id_seq'::regclass);


--
-- TOC entry 3841 (class 2604 OID 16538)
-- Name: platform_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_settings ALTER COLUMN id SET DEFAULT nextval('public.platform_settings_id_seq'::regclass);


--
-- TOC entry 3901 (class 2604 OID 17521)
-- Name: project_planning id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_planning ALTER COLUMN id SET DEFAULT nextval('public.project_planning_id_seq'::regclass);


--
-- TOC entry 3910 (class 2604 OID 17622)
-- Name: project_status_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_status_logs ALTER COLUMN id SET DEFAULT nextval('public.project_status_logs_id_seq'::regclass);


--
-- TOC entry 3904 (class 2604 OID 17550)
-- Name: project_tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks ALTER COLUMN id SET DEFAULT nextval('public.project_tasks_id_seq'::regclass);


--
-- TOC entry 3897 (class 2604 OID 17484)
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- TOC entry 3870 (class 2604 OID 17100)
-- Name: role_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions ALTER COLUMN id SET DEFAULT nextval('public.role_permissions_id_seq'::regclass);


--
-- TOC entry 3867 (class 2604 OID 17067)
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- TOC entry 3874 (class 2604 OID 17169)
-- Name: roles_features id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_features ALTER COLUMN id SET DEFAULT nextval('public.roles_features_id_seq'::regclass);


--
-- TOC entry 3908 (class 2604 OID 17593)
-- Name: task_updates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_updates ALTER COLUMN id SET DEFAULT nextval('public.task_updates_id_seq'::regclass);


--
-- TOC entry 3888 (class 2604 OID 17323)
-- Name: team_members id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_members ALTER COLUMN id SET DEFAULT nextval('public.team_members_id_seq'::regclass);


--
-- TOC entry 3885 (class 2604 OID 17295)
-- Name: teams id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams ALTER COLUMN id SET DEFAULT nextval('public.teams_id_seq'::regclass);


--
-- TOC entry 3877 (class 2604 OID 17213)
-- Name: user_profile_data id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profile_data ALTER COLUMN id SET DEFAULT nextval('public.user_profile_data_id_seq'::regclass);


--
-- TOC entry 3871 (class 2604 OID 17122)
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- TOC entry 3865 (class 2604 OID 17043)
-- Name: user_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN id SET DEFAULT nextval('public.user_sessions_id_seq'::regclass);


--
-- TOC entry 3861 (class 2604 OID 17020)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4006 (class 2606 OID 17253)
-- Name: attendance attendance_company_id_user_id_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_company_id_user_id_date_key UNIQUE (company_id, user_id, date);


--
-- TOC entry 4008 (class 2606 OID 17251)
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- TOC entry 3967 (class 2606 OID 16682)
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 3921 (class 2606 OID 16425)
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- TOC entry 3992 (class 2606 OID 17152)
-- Name: company_activity_logs company_activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_activity_logs
    ADD CONSTRAINT company_activity_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 3923 (class 2606 OID 16436)
-- Name: company_contacts company_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_contacts
    ADD CONSTRAINT company_contacts_pkey PRIMARY KEY (id);


--
-- TOC entry 3933 (class 2606 OID 16503)
-- Name: company_features company_features_company_id_feature_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_features
    ADD CONSTRAINT company_features_company_id_feature_id_key UNIQUE (company_id, feature_id);


--
-- TOC entry 3935 (class 2606 OID 16501)
-- Name: company_features company_features_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_features
    ADD CONSTRAINT company_features_pkey PRIMARY KEY (id);


--
-- TOC entry 3961 (class 2606 OID 16647)
-- Name: company_health_scores company_health_scores_company_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_health_scores
    ADD CONSTRAINT company_health_scores_company_id_key UNIQUE (company_id);


--
-- TOC entry 3963 (class 2606 OID 16645)
-- Name: company_health_scores company_health_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_health_scores
    ADD CONSTRAINT company_health_scores_pkey PRIMARY KEY (id);


--
-- TOC entry 3945 (class 2606 OID 16559)
-- Name: company_onboarding_logs company_onboarding_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_onboarding_logs
    ADD CONSTRAINT company_onboarding_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 3937 (class 2606 OID 16528)
-- Name: company_settings company_settings_company_id_setting_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_settings
    ADD CONSTRAINT company_settings_company_id_setting_key_key UNIQUE (company_id, setting_key);


--
-- TOC entry 3939 (class 2606 OID 16526)
-- Name: company_settings company_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_settings
    ADD CONSTRAINT company_settings_pkey PRIMARY KEY (id);


--
-- TOC entry 3927 (class 2606 OID 16465)
-- Name: company_subscriptions company_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_subscriptions
    ADD CONSTRAINT company_subscriptions_pkey PRIMARY KEY (id);


--
-- TOC entry 3949 (class 2606 OID 16592)
-- Name: company_usage_metrics company_usage_metrics_company_id_metric_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_usage_metrics
    ADD CONSTRAINT company_usage_metrics_company_id_metric_date_key UNIQUE (company_id, metric_date);


--
-- TOC entry 3951 (class 2606 OID 16590)
-- Name: company_usage_metrics company_usage_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_usage_metrics
    ADD CONSTRAINT company_usage_metrics_pkey PRIMARY KEY (id);


--
-- TOC entry 3998 (class 2606 OID 17203)
-- Name: feature_bundle_pages feature_bundle_pages_feature_id_page_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_bundle_pages
    ADD CONSTRAINT feature_bundle_pages_feature_id_page_code_key UNIQUE (feature_id, page_code);


--
-- TOC entry 4000 (class 2606 OID 17201)
-- Name: feature_bundle_pages feature_bundle_pages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_bundle_pages
    ADD CONSTRAINT feature_bundle_pages_pkey PRIMARY KEY (id);


--
-- TOC entry 3953 (class 2606 OID 16611)
-- Name: feature_usage_metrics feature_usage_metrics_company_id_feature_id_metric_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_usage_metrics
    ADD CONSTRAINT feature_usage_metrics_company_id_feature_id_metric_date_key UNIQUE (company_id, feature_id, metric_date);


--
-- TOC entry 3955 (class 2606 OID 16609)
-- Name: feature_usage_metrics feature_usage_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_usage_metrics
    ADD CONSTRAINT feature_usage_metrics_pkey PRIMARY KEY (id);


--
-- TOC entry 3929 (class 2606 OID 16489)
-- Name: features features_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.features
    ADD CONSTRAINT features_code_key UNIQUE (code);


--
-- TOC entry 3931 (class 2606 OID 16487)
-- Name: features features_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.features
    ADD CONSTRAINT features_pkey PRIMARY KEY (id);


--
-- TOC entry 4025 (class 2606 OID 17466)
-- Name: lead_interactions lead_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lead_interactions
    ADD CONSTRAINT lead_interactions_pkey PRIMARY KEY (id);


--
-- TOC entry 4022 (class 2606 OID 17421)
-- Name: leads leads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT leads_pkey PRIMARY KEY (id);


--
-- TOC entry 4010 (class 2606 OID 17274)
-- Name: leave_requests leave_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT leave_requests_pkey PRIMARY KEY (id);


--
-- TOC entry 3980 (class 2606 OID 17095)
-- Name: permissions permissions_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_code_key UNIQUE (code);


--
-- TOC entry 3982 (class 2606 OID 17093)
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 3925 (class 2606 OID 16451)
-- Name: plans plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT plans_pkey PRIMARY KEY (id);


--
-- TOC entry 3947 (class 2606 OID 16577)
-- Name: platform_activity_logs platform_activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_activity_logs
    ADD CONSTRAINT platform_activity_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 3917 (class 2606 OID 16410)
-- Name: platform_admins platform_admins_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_admins
    ADD CONSTRAINT platform_admins_email_key UNIQUE (email);


--
-- TOC entry 3919 (class 2606 OID 16408)
-- Name: platform_admins platform_admins_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_admins
    ADD CONSTRAINT platform_admins_pkey PRIMARY KEY (id);


--
-- TOC entry 3957 (class 2606 OID 16635)
-- Name: platform_revenue_metrics platform_revenue_metrics_metric_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_revenue_metrics
    ADD CONSTRAINT platform_revenue_metrics_metric_date_key UNIQUE (metric_date);


--
-- TOC entry 3959 (class 2606 OID 16633)
-- Name: platform_revenue_metrics platform_revenue_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_revenue_metrics
    ADD CONSTRAINT platform_revenue_metrics_pkey PRIMARY KEY (id);


--
-- TOC entry 3965 (class 2606 OID 16664)
-- Name: platform_sessions platform_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_sessions
    ADD CONSTRAINT platform_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 3941 (class 2606 OID 16548)
-- Name: platform_settings platform_settings_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_settings
    ADD CONSTRAINT platform_settings_key_key UNIQUE (key);


--
-- TOC entry 3943 (class 2606 OID 16546)
-- Name: platform_settings platform_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_settings
    ADD CONSTRAINT platform_settings_pkey PRIMARY KEY (id);


--
-- TOC entry 4029 (class 2606 OID 17533)
-- Name: project_planning project_planning_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_planning
    ADD CONSTRAINT project_planning_pkey PRIMARY KEY (id);


--
-- TOC entry 4031 (class 2606 OID 17535)
-- Name: project_planning project_planning_project_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_planning
    ADD CONSTRAINT project_planning_project_id_key UNIQUE (project_id);


--
-- TOC entry 4037 (class 2606 OID 17631)
-- Name: project_status_logs project_status_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_status_logs
    ADD CONSTRAINT project_status_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4033 (class 2606 OID 17563)
-- Name: project_tasks project_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT project_tasks_pkey PRIMARY KEY (id);


--
-- TOC entry 4027 (class 2606 OID 17494)
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- TOC entry 3984 (class 2606 OID 17105)
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 3986 (class 2606 OID 17107)
-- Name: role_permissions role_permissions_role_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_permission_id_key UNIQUE (role_id, permission_id);


--
-- TOC entry 3976 (class 2606 OID 17077)
-- Name: roles roles_company_id_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_company_id_name_key UNIQUE (company_id, name);


--
-- TOC entry 3994 (class 2606 OID 17174)
-- Name: roles_features roles_features_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_features
    ADD CONSTRAINT roles_features_pkey PRIMARY KEY (id);


--
-- TOC entry 3996 (class 2606 OID 17176)
-- Name: roles_features roles_features_role_id_feature_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_features
    ADD CONSTRAINT roles_features_role_id_feature_id_key UNIQUE (role_id, feature_id);


--
-- TOC entry 3978 (class 2606 OID 17075)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 4035 (class 2606 OID 17602)
-- Name: task_updates task_updates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_updates
    ADD CONSTRAINT task_updates_pkey PRIMARY KEY (id);


--
-- TOC entry 4016 (class 2606 OID 17330)
-- Name: team_members team_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_members
    ADD CONSTRAINT team_members_pkey PRIMARY KEY (id);


--
-- TOC entry 4012 (class 2606 OID 17306)
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (id);


--
-- TOC entry 4014 (class 2606 OID 17308)
-- Name: teams uq_team_name_per_company; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT uq_team_name_per_company UNIQUE (company_id, name);


--
-- TOC entry 4018 (class 2606 OID 17332)
-- Name: team_members uq_team_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_members
    ADD CONSTRAINT uq_team_user UNIQUE (team_id, user_id);


--
-- TOC entry 4002 (class 2606 OID 17222)
-- Name: user_profile_data user_profile_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profile_data
    ADD CONSTRAINT user_profile_data_pkey PRIMARY KEY (id);


--
-- TOC entry 4004 (class 2606 OID 17224)
-- Name: user_profile_data user_profile_data_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profile_data
    ADD CONSTRAINT user_profile_data_user_id_key UNIQUE (user_id);


--
-- TOC entry 3988 (class 2606 OID 17127)
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- TOC entry 3990 (class 2606 OID 17129)
-- Name: user_roles user_roles_user_id_role_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_role_id_key UNIQUE (user_id, role_id);


--
-- TOC entry 3974 (class 2606 OID 17052)
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 3970 (class 2606 OID 17033)
-- Name: users users_company_id_emp_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_company_id_emp_id_key UNIQUE (company_id, emp_id);


--
-- TOC entry 3972 (class 2606 OID 17031)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4023 (class 1259 OID 17479)
-- Name: idx_interactions_lead; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_interactions_lead ON public.lead_interactions USING btree (lead_id);


--
-- TOC entry 4019 (class 1259 OID 17477)
-- Name: idx_leads_assigned_employee; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_leads_assigned_employee ON public.leads USING btree (assigned_employee_id);


--
-- TOC entry 4020 (class 1259 OID 17478)
-- Name: idx_leads_follow_up; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_leads_follow_up ON public.leads USING btree (next_follow_up_date);


--
-- TOC entry 3968 (class 1259 OID 17164)
-- Name: uniq_company_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uniq_company_email ON public.users USING btree (company_id, email) WHERE (email IS NOT NULL);


--
-- TOC entry 4058 (class 2606 OID 17153)
-- Name: company_activity_logs company_activity_logs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_activity_logs
    ADD CONSTRAINT company_activity_logs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4059 (class 2606 OID 17158)
-- Name: company_activity_logs company_activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_activity_logs
    ADD CONSTRAINT company_activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 4038 (class 2606 OID 16437)
-- Name: company_contacts company_contacts_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_contacts
    ADD CONSTRAINT company_contacts_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4041 (class 2606 OID 16504)
-- Name: company_features company_features_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_features
    ADD CONSTRAINT company_features_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4042 (class 2606 OID 16509)
-- Name: company_features company_features_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_features
    ADD CONSTRAINT company_features_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id);


--
-- TOC entry 4048 (class 2606 OID 16648)
-- Name: company_health_scores company_health_scores_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_health_scores
    ADD CONSTRAINT company_health_scores_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4044 (class 2606 OID 16560)
-- Name: company_onboarding_logs company_onboarding_logs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_onboarding_logs
    ADD CONSTRAINT company_onboarding_logs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4043 (class 2606 OID 16529)
-- Name: company_settings company_settings_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_settings
    ADD CONSTRAINT company_settings_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4039 (class 2606 OID 16466)
-- Name: company_subscriptions company_subscriptions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_subscriptions
    ADD CONSTRAINT company_subscriptions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4040 (class 2606 OID 16471)
-- Name: company_subscriptions company_subscriptions_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_subscriptions
    ADD CONSTRAINT company_subscriptions_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.plans(id);


--
-- TOC entry 4045 (class 2606 OID 16593)
-- Name: company_usage_metrics company_usage_metrics_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_usage_metrics
    ADD CONSTRAINT company_usage_metrics_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4062 (class 2606 OID 17204)
-- Name: feature_bundle_pages feature_bundle_pages_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_bundle_pages
    ADD CONSTRAINT feature_bundle_pages_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE CASCADE;


--
-- TOC entry 4046 (class 2606 OID 16612)
-- Name: feature_usage_metrics feature_usage_metrics_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_usage_metrics
    ADD CONSTRAINT feature_usage_metrics_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4047 (class 2606 OID 16617)
-- Name: feature_usage_metrics feature_usage_metrics_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feature_usage_metrics
    ADD CONSTRAINT feature_usage_metrics_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id);


--
-- TOC entry 4063 (class 2606 OID 17230)
-- Name: user_profile_data fk_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profile_data
    ADD CONSTRAINT fk_company FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4072 (class 2606 OID 17512)
-- Name: leads fk_leads_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT fk_leads_company FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4065 (class 2606 OID 17275)
-- Name: leave_requests fk_leave_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT fk_leave_company FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 4066 (class 2606 OID 17285)
-- Name: leave_requests fk_leave_reviewer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT fk_leave_reviewer FOREIGN KEY (reviewed_by) REFERENCES public.users(id);


--
-- TOC entry 4067 (class 2606 OID 17280)
-- Name: leave_requests fk_leave_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leave_requests
    ADD CONSTRAINT fk_leave_user FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4080 (class 2606 OID 17541)
-- Name: project_planning fk_planning_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_planning
    ADD CONSTRAINT fk_planning_company FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 4081 (class 2606 OID 17536)
-- Name: project_planning fk_planning_project; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_planning
    ADD CONSTRAINT fk_planning_project FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- TOC entry 4090 (class 2606 OID 17637)
-- Name: project_status_logs fk_status_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_status_logs
    ADD CONSTRAINT fk_status_company FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 4091 (class 2606 OID 17632)
-- Name: project_status_logs fk_status_project; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_status_logs
    ADD CONSTRAINT fk_status_project FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- TOC entry 4092 (class 2606 OID 17642)
-- Name: project_status_logs fk_status_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_status_logs
    ADD CONSTRAINT fk_status_user FOREIGN KEY (changed_by) REFERENCES public.users(id);


--
-- TOC entry 4082 (class 2606 OID 17574)
-- Name: project_tasks fk_task_assigned_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT fk_task_assigned_user FOREIGN KEY (assigned_to) REFERENCES public.users(id);


--
-- TOC entry 4083 (class 2606 OID 17569)
-- Name: project_tasks fk_task_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT fk_task_company FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 4084 (class 2606 OID 17579)
-- Name: project_tasks fk_task_creator; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT fk_task_creator FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 4085 (class 2606 OID 17584)
-- Name: project_tasks fk_task_dependency; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT fk_task_dependency FOREIGN KEY (dependency_task_id) REFERENCES public.project_tasks(id);


--
-- TOC entry 4086 (class 2606 OID 17564)
-- Name: project_tasks fk_task_project; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_tasks
    ADD CONSTRAINT fk_task_project FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- TOC entry 4068 (class 2606 OID 17309)
-- Name: teams fk_team_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT fk_team_company FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 4069 (class 2606 OID 17314)
-- Name: teams fk_team_manager; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT fk_team_manager FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- TOC entry 4070 (class 2606 OID 17333)
-- Name: team_members fk_tm_team; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_members
    ADD CONSTRAINT fk_tm_team FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- TOC entry 4071 (class 2606 OID 17338)
-- Name: team_members fk_tm_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.team_members
    ADD CONSTRAINT fk_tm_user FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4087 (class 2606 OID 17608)
-- Name: task_updates fk_update_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_updates
    ADD CONSTRAINT fk_update_company FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 4088 (class 2606 OID 17603)
-- Name: task_updates fk_update_task; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_updates
    ADD CONSTRAINT fk_update_task FOREIGN KEY (task_id) REFERENCES public.project_tasks(id) ON DELETE CASCADE;


--
-- TOC entry 4089 (class 2606 OID 17613)
-- Name: task_updates fk_update_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_updates
    ADD CONSTRAINT fk_update_user FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- TOC entry 4064 (class 2606 OID 17225)
-- Name: user_profile_data fk_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profile_data
    ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4075 (class 2606 OID 17467)
-- Name: lead_interactions lead_interactions_lead_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lead_interactions
    ADD CONSTRAINT lead_interactions_lead_id_fkey FOREIGN KEY (lead_id) REFERENCES public.leads(id) ON DELETE CASCADE;


--
-- TOC entry 4076 (class 2606 OID 17472)
-- Name: lead_interactions lead_interactions_logged_by_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lead_interactions
    ADD CONSTRAINT lead_interactions_logged_by_employee_id_fkey FOREIGN KEY (logged_by_employee_id) REFERENCES public.users(id);


--
-- TOC entry 4073 (class 2606 OID 17422)
-- Name: leads leads_assigned_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT leads_assigned_employee_id_fkey FOREIGN KEY (assigned_employee_id) REFERENCES public.users(id);


--
-- TOC entry 4074 (class 2606 OID 17427)
-- Name: leads leads_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT leads_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- TOC entry 4049 (class 2606 OID 16665)
-- Name: platform_sessions platform_sessions_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.platform_sessions
    ADD CONSTRAINT platform_sessions_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.platform_admins(id) ON DELETE CASCADE;


--
-- TOC entry 4077 (class 2606 OID 17505)
-- Name: projects projects_assigned_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_assigned_team_id_fkey FOREIGN KEY (assigned_team_id) REFERENCES public.teams(id);


--
-- TOC entry 4078 (class 2606 OID 17495)
-- Name: projects projects_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- TOC entry 4079 (class 2606 OID 17500)
-- Name: projects projects_lead_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_lead_id_fkey FOREIGN KEY (lead_id) REFERENCES public.leads(id);


--
-- TOC entry 4054 (class 2606 OID 17113)
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- TOC entry 4055 (class 2606 OID 17108)
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- TOC entry 4053 (class 2606 OID 17078)
-- Name: roles roles_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4060 (class 2606 OID 17182)
-- Name: roles_features roles_features_feature_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_features
    ADD CONSTRAINT roles_features_feature_id_fkey FOREIGN KEY (feature_id) REFERENCES public.features(id) ON DELETE CASCADE;


--
-- TOC entry 4061 (class 2606 OID 17177)
-- Name: roles_features roles_features_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_features
    ADD CONSTRAINT roles_features_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- TOC entry 4056 (class 2606 OID 17135)
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- TOC entry 4057 (class 2606 OID 17130)
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4051 (class 2606 OID 17058)
-- Name: user_sessions user_sessions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- TOC entry 4052 (class 2606 OID 17053)
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4050 (class 2606 OID 17034)
-- Name: users users_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


-- Completed on 2026-02-08 06:26:46 IST

--
-- PostgreSQL database dump complete
--

\unrestrict CcG9HMSlhnvbSq2PpFcKvyfLRH4qvYsqTpVEgPmqUs7AUbddUSUv2JeFJC64gXi

