--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2
-- Dumped by pg_dump version 12.2

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: anncarters
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO anncarters;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: anncarters
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    from_id integer NOT NULL,
    for_id integer NOT NULL,
    text character varying(480) NOT NULL,
    date timestamp without time zone
);


ALTER TABLE public.messages OWNER TO anncarters;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: anncarters
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO anncarters;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: anncarters
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: anncarters
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    text character varying(480) NOT NULL,
    date timestamp without time zone,
    given_hugs integer
);


ALTER TABLE public.posts OWNER TO anncarters;

--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: anncarters
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posts_id_seq OWNER TO anncarters;

--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: anncarters
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: anncarters
--

CREATE TABLE public.users (
    id integer NOT NULL,
    auth0_id character varying NOT NULL,
    received_hugs integer,
    given_hugs integer,
    display_name character varying NOT NULL,
    login_count integer
);


ALTER TABLE public.users OWNER TO anncarters;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: anncarters
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO anncarters;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: anncarters
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: anncarters
--

COPY public.alembic_version (version_num) FROM stdin;
4822d58838df
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: anncarters
--

COPY public.messages (id, from_id, for_id, text, date) FROM stdin;
1	1	1	hang in there :)	2020-06-02 10:39:56.337
3	5	1	you'll be okay <3	2020-06-08 14:42:02.759
4	4	1	hiiii	2020-06-08 14:42:50.971
5	4	5	hellllllllo :)	2020-06-08 14:43:30.593
6	1	4	hiiii	2020-06-08 14:44:55.666
7	1	5	more testing	2020-06-08 14:45:05.713
8	5	4	hi there :)	2020-06-08 14:50:19.006
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: anncarters
--

COPY public.posts (id, user_id, text, date, given_hugs) FROM stdin;
4	1	test	2020-06-01 15:17:56.294	0
5	1	test	2020-06-01 15:18:37.305	0
6	1	test	2020-06-01 15:19:41.25	0
7	1	test	2020-06-01 15:20:11.927	0
2	1	test	2020-06-01 15:10:59.898	1
1	1	test	2020-06-01 15:05:01.966	1
9	1	leeeeeee b :))	2020-06-03 07:11:40.421	0
3	1	testing	2020-06-01 15:15:12.729	0
10	1	cutie baby lee	2020-06-04 07:56:09.791	0
11	1	baby lee :))	2020-06-04 08:15:50.811	1
12	5	new user	2020-06-08 14:07:25.297	0
13	5	2nd post	2020-06-08 14:30:58.88	0
14	4	new here	2020-06-08 14:43:05.574	0
15	4	testing user 3	2020-06-08 14:43:15.265	0
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: anncarters
--

COPY public.users (id, auth0_id, received_hugs, given_hugs, display_name, login_count) FROM stdin;
4	auth0|5ed8e3d0def75d0befbc7e50	0	0	user14	3
1	auth0|5ed34765f0b8e60c8e87ca62	2	2	shirb	57
5	auth0|5ede3e7a0793080013259050	0	0	user52	3
\.


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: anncarters
--

SELECT pg_catalog.setval('public.messages_id_seq', 8, true);


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: anncarters
--

SELECT pg_catalog.setval('public.posts_id_seq', 15, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: anncarters
--

SELECT pg_catalog.setval('public.users_id_seq', 5, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: messages messages_for_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_for_id_fkey FOREIGN KEY (for_id) REFERENCES public.users(id);


--
-- Name: messages messages_from_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_from_id_fkey FOREIGN KEY (from_id) REFERENCES public.users(id);


--
-- Name: posts posts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: anncarters
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

