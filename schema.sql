CREATE TABLE IF NOT EXISTS public.news_analysis
(
    news_url text COLLATE pg_catalog."default" NOT NULL,
    reliability_score numeric(5,2) NOT NULL,
    source_score numeric(5,2) NOT NULL,
    provocation_score numeric(5,2) NOT NULL,
    CONSTRAINT news_analysis_news_url_key UNIQUE (news_url)
);
CREATE TABLE IF NOT EXISTS public.other_sources
(
    source_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    true_news integer DEFAULT 0,
    fake_news integer DEFAULT 0,
    reliability_score numeric(5,2) GENERATED ALWAYS AS (((true_news)::numeric / ((true_news + fake_news))::numeric)) STORED,
    CONSTRAINT other_sources_source_name_key UNIQUE (source_name)
);
CREATE TABLE IF NOT EXISTS public.reliable_sources
(
    id integer NOT NULL DEFAULT nextval('reliable_sources_id_seq'::regclass),
    source_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT reliable_sources_pkey PRIMARY KEY (id),
    CONSTRAINT reliable_sources_source_name_key UNIQUE (source_name)
);
CREATE TABLE IF NOT EXISTS public.satirical_sources
(
    id integer NOT NULL DEFAULT nextval('satirical_sources_id_seq'::regclass),
    source_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT satirical_sources_pkey PRIMARY KEY (id),
    CONSTRAINT satirical_sources_source_name_key UNIQUE (source_name)
);
CREATE TABLE IF NOT EXISTS public.unreliable_sources
(
    id integer NOT NULL DEFAULT nextval('unreliable_sources_id_seq'::regclass),
    source_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT unreliable_sources_pkey PRIMARY KEY (id),
    CONSTRAINT unreliable_sources_source_name_key UNIQUE (source_name)
);