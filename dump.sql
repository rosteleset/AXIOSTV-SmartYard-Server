--
-- PostgreSQL database dump
--

-- Dumped from database version 10.19
-- Dumped by pg_dump version 10.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: citext; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;


--
-- Name: EXTENSION citext; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION citext IS 'data type for case-insensitive character strings';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO smartyard;

--
-- Name: devices; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.devices (
    device_id integer NOT NULL,
    device_uuid uuid NOT NULL,
    device_mac macaddr,
    device_type integer NOT NULL,
    affiliation integer,
    owner integer,
    url character varying(64),
    port integer,
    stream character varying(64),
    is_active boolean DEFAULT false,
    title character varying(64),
    address character varying(110),
    longitude numeric(12,9),
    latitude numeric(12,9),
    server_id integer,
    tariff_id integer,
    domophoneid integer,
    sippassword text,
    dtmf integer,
    camshot text
);


ALTER TABLE public.devices OWNER TO smartyard;

--
-- Name: devices_device_id_seq; Type: SEQUENCE; Schema: public; Owner: smartyard
--

CREATE SEQUENCE public.devices_device_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devices_device_id_seq OWNER TO smartyard;

--
-- Name: devices_device_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartyard
--

ALTER SEQUENCE public.devices_device_id_seq OWNED BY public.devices.device_id;


--
-- Name: doors; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.doors (
    id integer NOT NULL,
    open character varying(128) NOT NULL,
    device_id integer NOT NULL,
    cam integer NOT NULL,
    icon character varying(14),
    entrance integer,
    name text
);


ALTER TABLE public.doors OWNER TO smartyard;

--
-- Name: doors_id_seq; Type: SEQUENCE; Schema: public; Owner: smartyard
--

CREATE SEQUENCE public.doors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.doors_id_seq OWNER TO smartyard;

--
-- Name: doors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartyard
--

ALTER SEQUENCE public.doors_id_seq OWNED BY public.doors.id;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.invoices (
    invoice_id integer NOT NULL,
    invoice_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    invoice_pay boolean DEFAULT false,
    contract text
);


ALTER TABLE public.invoices OWNER TO smartyard;

--
-- Name: invoices_invoice_id_seq; Type: SEQUENCE; Schema: public; Owner: smartyard
--

CREATE SEQUENCE public.invoices_invoice_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invoices_invoice_id_seq OWNER TO smartyard;

--
-- Name: invoices_invoice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartyard
--

ALTER SEQUENCE public.invoices_invoice_id_seq OWNED BY public.invoices.invoice_id;


--
-- Name: records; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.records (
    id integer NOT NULL,
    uid integer,
    url text,
    fileurl text,
    rtime timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    rdone boolean DEFAULT false
);


ALTER TABLE public.records OWNER TO smartyard;

--
-- Name: records_id_seq; Type: SEQUENCE; Schema: public; Owner: smartyard
--

CREATE SEQUENCE public.records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.records_id_seq OWNER TO smartyard;

--
-- Name: records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartyard
--

ALTER SEQUENCE public.records_id_seq OWNED BY public.records.id;


--
-- Name: rights; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.rights (
    uid integer NOT NULL,
    uid_right integer[]
);


ALTER TABLE public.rights OWNER TO smartyard;

--
-- Name: settings; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.settings (
    uid integer NOT NULL,
    intercom boolean DEFAULT true NOT NULL,
    asterisk boolean DEFAULT true NOT NULL,
    w_rabbit boolean DEFAULT false NOT NULL,
    frs boolean DEFAULT true NOT NULL,
    code integer,
    guest timestamp without time zone
);


ALTER TABLE public.settings OWNER TO smartyard;

--
-- Name: temps; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.temps (
    userphone bigint NOT NULL,
    smscode integer
);


ALTER TABLE public.temps OWNER TO smartyard;

--
-- Name: temps_userphone_seq; Type: SEQUENCE; Schema: public; Owner: smartyard
--

CREATE SEQUENCE public.temps_userphone_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.temps_userphone_seq OWNER TO smartyard;

--
-- Name: temps_userphone_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartyard
--

ALTER SEQUENCE public.temps_userphone_seq OWNED BY public.temps.userphone;


--
-- Name: types; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.types (
    id integer NOT NULL,
    type character varying(64) NOT NULL
);


ALTER TABLE public.types OWNER TO smartyard;

--
-- Name: types_id_seq; Type: SEQUENCE; Schema: public; Owner: smartyard
--

CREATE SEQUENCE public.types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.types_id_seq OWNER TO smartyard;

--
-- Name: types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: smartyard
--

ALTER SEQUENCE public.types_id_seq OWNED BY public.types.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: smartyard
--

CREATE TABLE public.users (
    uuid uuid NOT NULL,
    userphone bigint,
    name character varying(24),
    patronymic character varying(24),
    email character varying(60),
    videotoken character varying(32),
    vttime timestamp without time zone,
    strims text[],
    pushtoken text,
    platform text,
    version text,
    uid integer,
    notify boolean DEFAULT true NOT NULL,
    money boolean DEFAULT true NOT NULL
);


ALTER TABLE public.users OWNER TO smartyard;

--
-- Name: devices device_id; Type: DEFAULT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.devices ALTER COLUMN device_id SET DEFAULT nextval('public.devices_device_id_seq'::regclass);


--
-- Name: doors id; Type: DEFAULT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.doors ALTER COLUMN id SET DEFAULT nextval('public.doors_id_seq'::regclass);


--
-- Name: invoices invoice_id; Type: DEFAULT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.invoices ALTER COLUMN invoice_id SET DEFAULT nextval('public.invoices_invoice_id_seq'::regclass);


--
-- Name: records id; Type: DEFAULT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.records ALTER COLUMN id SET DEFAULT nextval('public.records_id_seq'::regclass);


--
-- Name: temps userphone; Type: DEFAULT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.temps ALTER COLUMN userphone SET DEFAULT nextval('public.temps_userphone_seq'::regclass);


--
-- Name: types id; Type: DEFAULT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.types ALTER COLUMN id SET DEFAULT nextval('public.types_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: devices devices_device_uuid_key; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_device_uuid_key UNIQUE (device_uuid);


--
-- Name: devices devices_domophoneid_key; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_domophoneid_key UNIQUE (domophoneid);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (device_id);


--
-- Name: doors doors_pkey; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.doors
    ADD CONSTRAINT doors_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (invoice_id);


--
-- Name: records records_fileurl_key; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.records
    ADD CONSTRAINT records_fileurl_key UNIQUE (fileurl);


--
-- Name: records records_pkey; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.records
    ADD CONSTRAINT records_pkey PRIMARY KEY (id);


--
-- Name: records records_url_key; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.records
    ADD CONSTRAINT records_url_key UNIQUE (url);


--
-- Name: rights rights_pkey; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.rights
    ADD CONSTRAINT rights_pkey PRIMARY KEY (uid);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (uid);


--
-- Name: temps temps_pkey; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.temps
    ADD CONSTRAINT temps_pkey PRIMARY KEY (userphone);


--
-- Name: types types_pkey; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.types
    ADD CONSTRAINT types_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (uuid);


--
-- Name: ix_temps_smscode; Type: INDEX; Schema: public; Owner: smartyard
--

CREATE UNIQUE INDEX ix_temps_smscode ON public.temps USING btree (smscode);


--
-- Name: ix_users_userphone; Type: INDEX; Schema: public; Owner: smartyard
--

CREATE UNIQUE INDEX ix_users_userphone ON public.users USING btree (userphone);


--
-- Name: devices devices_device_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_device_type_fkey FOREIGN KEY (device_type) REFERENCES public.types(id) ON DELETE CASCADE;


--
-- Name: doors doors_address_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.doors
    ADD CONSTRAINT doors_address_fkey FOREIGN KEY (device_id) REFERENCES public.devices(device_id) ON DELETE CASCADE;


--
-- Name: doors doors_cam_fkey; Type: FK CONSTRAINT; Schema: public; Owner: smartyard
--

ALTER TABLE ONLY public.doors
    ADD CONSTRAINT doors_cam_fkey FOREIGN KEY (cam) REFERENCES public.devices(device_id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA public TO smartyard;


--
-- PostgreSQL database dump complete
--
