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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: shirbarlev
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO shirbarlev;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: shirbarlev
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    from_id integer NOT NULL,
    for_id integer NOT NULL,
    text character varying(480) NOT NULL,
    date timestamp without time zone,
    thread integer NOT NULL,
    for_deleted boolean NOT NULL,
    from_deleted boolean NOT NULL
);


ALTER TABLE public.messages OWNER TO shirbarlev;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: shirbarlev
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO shirbarlev;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: shirbarlev
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: shirbarlev
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    for_id integer NOT NULL,
    from_id integer NOT NULL,
    type character varying NOT NULL,
    text character varying NOT NULL,
    date timestamp without time zone NOT NULL
);


ALTER TABLE public.notifications OWNER TO shirbarlev;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: shirbarlev
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notifications_id_seq OWNER TO shirbarlev;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: shirbarlev
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: shirbarlev
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    text character varying(480) NOT NULL,
    date timestamp without time zone,
    given_hugs integer,
    open_report boolean NOT NULL,
    sent_hugs text
);


ALTER TABLE public.posts OWNER TO shirbarlev;

--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: shirbarlev
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posts_id_seq OWNER TO shirbarlev;

--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: shirbarlev
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: shirbarlev
--

CREATE TABLE public.reports (
    id integer NOT NULL,
    type character varying(10) NOT NULL,
    user_id integer NOT NULL,
    post_id integer,
    reporter integer NOT NULL,
    report_reason character varying(480) NOT NULL,
    dismissed boolean NOT NULL,
    closed boolean NOT NULL,
    date timestamp without time zone
);


ALTER TABLE public.reports OWNER TO shirbarlev;

--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: shirbarlev
--

CREATE SEQUENCE public.reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reports_id_seq OWNER TO shirbarlev;

--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: shirbarlev
--

ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: shirbarlev
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    "user" integer NOT NULL,
    endpoint character varying NOT NULL,
    subscription_data text NOT NULL
);


ALTER TABLE public.subscriptions OWNER TO shirbarlev;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: shirbarlev
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscriptions_id_seq OWNER TO shirbarlev;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: shirbarlev
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: threads; Type: TABLE; Schema: public; Owner: shirbarlev
--

CREATE TABLE public.threads (
    id integer NOT NULL,
    user_1_id integer NOT NULL,
    user_2_id integer NOT NULL,
    user_1_deleted boolean NOT NULL,
    user_2_deleted boolean NOT NULL
);


ALTER TABLE public.threads OWNER TO shirbarlev;

--
-- Name: threads_id_seq; Type: SEQUENCE; Schema: public; Owner: shirbarlev
--

CREATE SEQUENCE public.threads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.threads_id_seq OWNER TO shirbarlev;

--
-- Name: threads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: shirbarlev
--

ALTER SEQUENCE public.threads_id_seq OWNED BY public.threads.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: shirbarlev
--

CREATE TABLE public.users (
    id integer NOT NULL,
    auth0_id character varying NOT NULL,
    received_hugs integer,
    given_hugs integer,
    display_name character varying NOT NULL,
    login_count integer,
    role character varying,
    blocked boolean NOT NULL,
    open_report boolean NOT NULL,
    release_date timestamp without time zone,
    last_notifications_read timestamp without time zone,
    auto_refresh boolean,
    push_enabled boolean,
    refresh_rate integer
);


ALTER TABLE public.users OWNER TO shirbarlev;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: shirbarlev
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO shirbarlev;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: shirbarlev
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Name: reports id; Type: DEFAULT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.reports ALTER COLUMN id SET DEFAULT nextval('public.reports_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: threads id; Type: DEFAULT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.threads ALTER COLUMN id SET DEFAULT nextval('public.threads_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: shirbarlev
--

COPY public.alembic_version (version_num) FROM stdin;
97ebcd9c039d
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: shirbarlev
--

COPY public.messages (id, from_id, for_id, text, date, thread, for_deleted, from_deleted) FROM stdin;
18	4	4	Your post (ID 19) was deleted due to violating our community rules.	2020-06-22 14:32:38.056	4	t	f
5	4	5	hellllllllo :)	2020-06-08 14:43:30.593	4	f	t
8	5	4	hi there :)	2020-06-08 14:50:19.006	4	t	f
10	4	1	hi :)	2020-06-14 14:07:37.49	4	f	t
19	4	4	Your post (ID 20) was deleted due to violating our community rules.	2020-06-22 14:34:58.019	4	t	t
1	1	1	hang in there :)	2020-06-02 10:39:56.337	1	f	f
3	5	1	you'll be okay <3	2020-06-08 14:42:02.759	2	f	f
7	1	5	more testing	2020-06-08 14:45:05.713	2	f	f
9	4	1	hang in there	2020-06-08 14:43:15	3	f	f
16	9	5	hiiiii	2020-06-14 14:25:37.569	6	f	f
20	4	4	Your post (ID 21) was deleted due to violating our community rules.	2020-06-22 20:41:12.213	4	t	t
21	4	1	hi	2020-07-06 17:33:55.712	4	f	f
22	4	1	test	2020-07-06 17:40:51.288	4	f	f
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: shirbarlev
--

COPY public.notifications (id, for_id, from_id, type, text, date) FROM stdin;
1	4	4	hug	You got a hug	2020-07-08 13:05:21.045101
2	4	4	hug	You got a hug	2020-07-08 13:06:14.900956
3	4	4	hug	You got a hug	2020-07-08 13:06:46.626559
4	4	4	hug	You got a hug	2020-07-08 13:14:32.762052
5	4	4	hug	You got a hug	2020-07-08 13:21:54.464433
6	4	4	hug	You got a hug	2020-07-08 18:37:35.118498
7	4	4	hug	You got a hug	2020-07-08 18:42:37.632753
8	4	4	hug	You got a hug	2020-07-08 18:57:28.370055
9	4	4	hug	You got a hug	2020-07-08 19:30:17.662651
10	4	4	hug	You got a hug	2020-07-08 19:34:20.655902
11	4	4	hug	You got a hug	2020-07-08 20:10:30.903444
12	4	4	hug	You got a hug	2020-07-08 20:30:46.662853
13	4	4	hug	You got a hug	2020-07-08 20:53:58.684166
14	4	4	hug	You got a hug	2020-07-08 21:02:28.006988
15	4	4	hug	You got a hug	2020-07-08 21:03:53.611889
16	4	4	hug	You got a hug	2020-07-09 11:55:51.856126
17	4	4	hug	You got a hug	2020-07-09 12:14:16.781994
18	4	4	hug	You got a hug	2020-07-09 12:17:19.870488
19	4	4	hug	You got a hug	2020-07-09 12:20:40.981412
20	4	4	hug	You got a hug	2020-07-09 13:03:50.612026
21	4	4	hug	You got a hug	2020-07-09 13:18:52.64558
22	4	4	hug	You got a hug	2020-07-09 13:22:14.386318
23	4	4	hug	You got a hug	2020-07-09 13:26:26.147308
24	4	4	hug	You got a hug	2020-07-09 13:46:58.322147
25	4	4	hug	You got a hug	2020-07-09 13:49:59.420843
26	4	4	hug	You got a hug	2020-07-09 13:53:31.563989
27	4	4	hug	You got a hug	2020-07-09 14:39:37.324127
28	4	4	hug	You got a hug	2020-07-09 15:57:50.574972
29	4	4	hug	You got a hug	2020-07-13 16:06:07.646147
30	4	4	hug	You got a hug	2020-07-13 16:09:47.367847
31	4	4	hug	You got a hug	2020-07-13 16:12:23.553046
32	4	4	hug	You got a hug	2020-07-13 16:14:33.286915
33	4	4	hug	You got a hug	2020-07-13 17:52:00.180463
34	4	4	hug	You got a hug	2020-07-13 17:52:54.081449
35	4	4	hug	You got a hug	2020-07-13 21:18:54.994732
36	4	4	hug	You got a hug	2020-07-13 21:31:14.229423
37	4	4	hug	You got a hug	2020-07-13 21:32:58.786522
38	4	4	hug	You got a hug	2020-07-13 21:35:48.566696
39	4	4	hug	You got a hug	2020-07-13 21:36:02.392095
40	4	4	hug	You got a hug	2020-07-13 21:36:12.524953
41	4	4	hug	You got a hug	2020-07-14 11:30:07.354089
42	4	4	hug	You got a hug	2020-07-14 11:30:12.560007
43	4	4	hug	You got a hug	2020-07-14 11:55:51.240234
44	4	4	hug	You got a hug	2020-07-14 13:02:42.709881
45	4	4	hug	You got a hug	2020-07-14 13:08:21.978572
46	1	4	hug	You got a hug	2020-07-14 16:00:41.414829
47	4	4	hug	You got a hug	2020-07-14 16:00:48.658501
48	4	4	hug	You got a hug	2020-07-14 16:00:52.290504
49	4	4	hug	You got a hug	2020-07-14 16:00:57.635331
50	4	4	hug	You got a hug	2020-07-20 17:30:57.513678
51	4	4	hug	You got a hug	2020-07-20 17:31:18.728888
52	4	4	hug	You got a hug	2020-07-20 17:31:45.554583
53	4	4	hug	You got a hug	2020-07-20 17:32:19.808169
54	4	4	hug	You got a hug	2020-07-21 14:35:20.297422
55	4	4	hug	You got a hug	2020-07-21 14:35:34.933279
56	4	4	hug	You got a hug	2020-07-21 14:36:00.316687
57	4	4	hug	You got a hug	2020-07-21 14:36:05.76754
58	4	4	hug	You got a hug	2020-07-22 11:38:02.864273
59	4	4	hug	You got a hug	2020-07-22 11:39:45.109452
60	4	4	hug	You got a hug	2020-07-22 11:45:57.699555
61	4	4	hug	You got a hug	2020-07-22 11:47:10.258195
62	4	4	hug	You got a hug	2020-07-22 12:16:14.657724
63	4	4	hug	You got a hug	2020-07-22 12:18:54.286811
64	4	4	hug	You got a hug	2020-07-22 12:22:00.067407
65	4	4	hug	You got a hug	2020-07-22 12:22:54.884349
66	4	4	hug	You got a hug	2020-07-22 12:23:21.062704
67	4	4	hug	You got a hug	2020-07-22 12:37:08.019144
68	4	4	hug	You got a hug	2020-07-22 13:20:59.398594
69	4	4	hug	You got a hug	2020-07-22 13:36:52.419098
70	1	4	hug	You got a hug	2020-07-22 13:40:25.495938
71	1	4	hug	You got a hug	2020-07-22 13:41:51.227895
72	4	4	hug	You got a hug	2020-07-22 13:42:35.797629
73	5	4	hug	You got a hug	2020-07-22 13:42:40.059274
74	1	4	hug	You got a hug	2020-07-22 13:42:44.75568
75	1	4	hug	You got a hug	2020-07-22 14:09:01.457204
76	1	4	hug	You got a hug	2020-07-22 15:01:45.393836
77	1	4	hug	You got a hug	2020-07-22 15:09:58.206196
78	1	4	hug	You got a hug	2020-07-22 15:18:49.469451
79	4	4	hug	You got a hug	2020-07-22 15:30:06.395028
80	5	4	hug	You got a hug	2020-08-10 19:40:21.244178
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: shirbarlev
--

COPY public.posts (id, user_id, text, date, given_hugs, open_report, sent_hugs) FROM stdin;
30	4	hello :)	2020-07-18 12:11:39.65	24	f	4 
28	4	testing2	2020-07-13 18:43:51.255	9	f	4 
26	4	testing new design	2020-07-13 18:40:34.806	1	f	4 
6	1	testing	2020-06-01 15:19:41.25	1	f	4 
11	1	baby lee :))	2020-06-04 08:15:50.811	2	f	4 
22	4	testing service worker	2020-06-27 10:31:24.915	1	f	4 
13	5	2nd post	2020-06-08 14:30:58.88	1	f	4 
10	1	cutie baby lee	2020-06-04 07:56:09.791	1	f	4 
5	1	testing update	2020-06-01 15:18:37.305	1	f	4 
7	1	testing #2	2020-06-01 15:20:11.927	1	f	4 
2	1	test	2020-06-01 15:10:59.898	2	f	4 
4	1	test	2020-06-01 15:17:56.294	2	f	4 
23	4	post	2020-06-27 19:17:31.072	2	f	4 
12	5	new user	2020-06-08 14:07:25.297	1	f	4 
1	1	test	2020-06-01 15:05:01.966	1	f	
9	1	leeeeeee b :))	2020-06-03 07:11:40.421	0	f	
25	4	for report	2020-07-06 08:02:02.184	66	f	
\.


--
-- Data for Name: reports; Type: TABLE DATA; Schema: public; Owner: shirbarlev
--

COPY public.reports (id, type, user_id, post_id, reporter, report_reason, dismissed, closed, date) FROM stdin;
1	Post	1	9	4	The post is Inappropriate	t	t	2020-06-22 13:38:58.052
2	Post	1	11	4	The post is Inappropriate	t	t	2020-06-22 14:08:10.401
3	Post	4	\N	4	The post is Inappropriate	f	f	2020-06-22 14:13:25.667
4	Post	4	\N	4	The post is Inappropriate	f	f	2020-06-22 14:30:33.051
26	Post	4	\N	4	The post is Spam	t	t	2020-06-22 20:09:42.139
5	Post	4	\N	4	The post is Inappropriate	t	t	2020-06-22 14:34:46.527
6	User	5	\N	4	The user is posting Spam	t	t	2020-06-22 14:41:30.361
7	User	5	\N	4	The user is posting Spam	t	t	2020-06-22 15:03:27.242
8	Post	1	9	4	The post is Inappropriate	t	t	2020-06-22 16:27:32.399
9	Post	1	9	4	The post is Inappropriate	t	t	2020-06-22 16:31:45.47
10	Post	4	\N	4	The post is Inappropriate	t	t	2020-06-22 16:42:40.316
11	Post	4	\N	4	The post is Inappropriate	t	t	2020-06-22 16:44:17.816
12	Post	4	\N	4	The post is Spam	t	t	2020-06-22 19:30:00.082
13	Post	4	\N	4	The post is Inappropriate	t	t	2020-06-22 19:31:40.851
14	Post	4	\N	4	The post is Spam	t	t	2020-06-22 19:32:25.102
15	Post	4	\N	4	The post is Offensive	t	t	2020-06-22 19:53:04.05
16	Post	4	\N	4	The post is Offensive	t	t	2020-06-22 19:54:08.875
17	Post	4	\N	4	The post is Offensive	t	t	2020-06-22 19:55:17.798
18	Post	4	\N	4	The post is Inappropriate	t	t	2020-06-22 19:57:20.996
19	Post	4	\N	4	The post is Inappropriate	t	t	2020-06-22 19:59:34.313
20	Post	4	\N	4	The post is Spam	t	t	2020-06-22 20:00:24.779
21	Post	4	\N	4	The post is Offensive	t	t	2020-06-22 20:03:32.287
22	Post	4	\N	4	The post is Spam	t	t	2020-06-22 20:04:34.395
23	Post	4	\N	4	The post is Spam	t	t	2020-06-22 20:05:31.173
24	Post	4	\N	4	The post is Offensive	t	t	2020-06-22 20:07:16.256
25	Post	4	\N	4	The post is Spam	t	t	2020-06-22 20:08:09.871
27	Post	4	\N	4	The post is Offensive	f	t	2020-06-22 20:10:45.884
28	Post	4	\N	4	The post is Offensive	f	t	2020-06-22 20:11:24.518
29	Post	4	\N	4	The post is Offensive	f	t	2020-06-22 20:13:27.256
30	Post	4	\N	4	The post is Inappropriate	t	t	2020-06-22 20:18:46.182
31	Post	4	\N	4	The post is Offensive	t	t	2020-06-22 20:27:24.199
32	Post	4	\N	4	The post is Offensive	f	t	2020-06-22 20:34:40.16
33	Post	4	\N	4	The post is Offensive	f	t	2020-06-22 20:36:13.622
34	Post	4	\N	4	The post is Spam	t	t	2020-06-22 20:40:57.717
35	User	5	\N	4	The user is posting Spam	t	t	2020-06-22 20:41:47.885
36	Post	4	25	4		t	t	2020-07-06 08:14:31.918
37	Post	4	25	4	The post is Inappropriate	t	t	2020-07-06 10:02:46.046
38	Post	4	25	4		t	t	2020-07-06 10:10:34.082
41	Post	4	25	4		t	t	2020-07-06 10:17:29.549
40	Post	4	25	4		t	t	2020-07-06 10:17:21.702
39	Post	4	25	4		t	t	2020-07-06 10:15:07.428
42	Post	4	25	4	gffdsgfd	t	t	2020-07-06 10:20:37.963
43	Post	4	25	4	testing	t	t	2020-07-06 10:36:53.98
44	Post	4	28	4	The post is Inappropriate	t	t	2020-07-13 19:13:48.279
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: shirbarlev
--

COPY public.subscriptions (id, "user", endpoint, subscription_data) FROM stdin;
\.


--
-- Data for Name: threads; Type: TABLE DATA; Schema: public; Owner: shirbarlev
--

COPY public.threads (id, user_1_id, user_2_id, user_1_deleted, user_2_deleted) FROM stdin;
1	1	1	f	f
2	1	5	f	f
3	1	4	f	f
6	9	5	f	f
4	4	5	t	f
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: shirbarlev
--

COPY public.users (id, auth0_id, received_hugs, given_hugs, display_name, login_count, role, blocked, open_report, release_date, last_notifications_read, auto_refresh, push_enabled, refresh_rate) FROM stdin;
9	auth0|5edf7b060793080013276746	0	1	user93	2	admin	f	f	\N	\N	\N	\N	\N
4	auth0|5ed8e3d0def75d0befbc7e50	97	106	user14	32	admin	f	f	\N	2020-09-04 12:43:11.613438	f	t	\N
20	auth0|5f4b9fd9915cd400670f4633	0	0	user24	2	user	t	f	2120-08-11 08:33:22.473	2020-09-04 11:19:24.680191	f	f	0
1	auth0|5ed34765f0b8e60c8e87ca62	10	2	shirb	60	admin	f	f	\N	\N	\N	\N	\N
5	auth0|5ede3e7a0793080013259050	2	0	user52	7	moderator	f	f	\N	\N	\N	\N	\N
\.


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: shirbarlev
--

SELECT pg_catalog.setval('public.messages_id_seq', 22, true);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: shirbarlev
--

SELECT pg_catalog.setval('public.notifications_id_seq', 80, true);


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: shirbarlev
--

SELECT pg_catalog.setval('public.posts_id_seq', 31, true);


--
-- Name: reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: shirbarlev
--

SELECT pg_catalog.setval('public.reports_id_seq', 44, true);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: shirbarlev
--

SELECT pg_catalog.setval('public.subscriptions_id_seq', 9, true);


--
-- Name: threads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: shirbarlev
--

SELECT pg_catalog.setval('public.threads_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: shirbarlev
--

SELECT pg_catalog.setval('public.users_id_seq', 20, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: threads threads_pkey; Type: CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.threads
    ADD CONSTRAINT threads_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: messages messages_for_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_for_id_fkey FOREIGN KEY (for_id) REFERENCES public.users(id);


--
-- Name: messages messages_from_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_from_id_fkey FOREIGN KEY (from_id) REFERENCES public.users(id);


--
-- Name: messages messages_thread_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_thread_fkey FOREIGN KEY (thread) REFERENCES public.threads(id);


--
-- Name: notifications notifications_for_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_for_id_fkey FOREIGN KEY (for_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_from_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_from_id_fkey FOREIGN KEY (from_id) REFERENCES public.users(id);


--
-- Name: posts posts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: reports reports_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: reports reports_reporter_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_reporter_fkey FOREIGN KEY (reporter) REFERENCES public.users(id);


--
-- Name: reports reports_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: subscriptions subscriptions_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_fkey FOREIGN KEY ("user") REFERENCES public.users(id);


--
-- Name: threads threads_user_1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.threads
    ADD CONSTRAINT threads_user_1_id_fkey FOREIGN KEY (user_1_id) REFERENCES public.users(id);


--
-- Name: threads threads_user_2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: shirbarlev
--

ALTER TABLE ONLY public.threads
    ADD CONSTRAINT threads_user_2_id_fkey FOREIGN KEY (user_2_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

