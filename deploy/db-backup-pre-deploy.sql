--
-- PostgreSQL database dump
--

\restrict Uiy6BIPggxkkRgQLXG03H5ego6UebqHAjDmwQWnlXCNms58lE9gi2Px6QwvtMbD

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg12+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg12+1)

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
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: achievements; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.achievements (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    achievement_id character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    icon_url text,
    unlocked_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.achievements OWNER TO isekai;

--
-- Name: affection; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.affection (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    character_id uuid NOT NULL,
    value integer,
    level character varying(20),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.affection OWNER TO isekai;

--
-- Name: affection_history; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.affection_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    character_id uuid NOT NULL,
    delta integer NOT NULL,
    old_value integer NOT NULL,
    new_value integer NOT NULL,
    old_level character varying(20) NOT NULL,
    new_level character varying(20) NOT NULL,
    reason character varying(50) DEFAULT 'choice'::character varying NOT NULL,
    source_session_id uuid,
    source_choice_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.affection_history OWNER TO isekai;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO isekai;

--
-- Name: cg_assets; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.cg_assets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    script_id uuid NOT NULL,
    route_id uuid,
    name character varying(255) NOT NULL,
    image_url text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.cg_assets OWNER TO isekai;

--
-- Name: character_memories; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.character_memories (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    character_id uuid,
    memory_text text NOT NULL,
    embedding public.vector(1536),
    source_session_id uuid,
    confidence numeric(3,2),
    is_compressed boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    source character varying(50) DEFAULT 'game_event'::character varying NOT NULL
);


ALTER TABLE public.character_memories OWNER TO isekai;

--
-- Name: character_sprites; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.character_sprites (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    character_id uuid NOT NULL,
    emotion character varying(50) NOT NULL,
    image_url text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.character_sprites OWNER TO isekai;

--
-- Name: characters; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.characters (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    script_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    dialogue_style character varying(50),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.characters OWNER TO isekai;

--
-- Name: collections; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.collections (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    item_type character varying(50) NOT NULL,
    item_id character varying(100) NOT NULL,
    item_name character varying(255) NOT NULL,
    image_url text,
    unlocked_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.collections OWNER TO isekai;

--
-- Name: comments; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.comments (
    id uuid NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    content text NOT NULL,
    is_deleted boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.comments OWNER TO isekai;

--
-- Name: daily_checkins; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.daily_checkins (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    date date NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.daily_checkins OWNER TO isekai;

--
-- Name: daily_tasks; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.daily_tasks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    date date NOT NULL,
    task_type character varying(50) NOT NULL,
    progress integer,
    target integer,
    completed boolean,
    claimed boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.daily_tasks OWNER TO isekai;

--
-- Name: email_verifications; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.email_verifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    token character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.email_verifications OWNER TO isekai;

--
-- Name: fragment_transactions; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.fragment_transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    amount integer NOT NULL,
    reason character varying(100) NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.fragment_transactions OWNER TO isekai;

--
-- Name: fragments; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.fragments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    balance integer,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.fragments OWNER TO isekai;

--
-- Name: game_progress; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.game_progress (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_id uuid NOT NULL,
    node_id uuid NOT NULL,
    choice_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.game_progress OWNER TO isekai;

--
-- Name: game_sessions; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.game_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    script_id uuid NOT NULL,
    route_id uuid NOT NULL,
    current_node_id uuid,
    status character varying(20),
    custom_name character varying(12),
    avatar_choice character varying(50),
    started_at timestamp with time zone DEFAULT now(),
    completed_at timestamp with time zone,
    ending_type character varying(20),
    choice_history json,
    metadata json
);


ALTER TABLE public.game_sessions OWNER TO isekai;

--
-- Name: node_choices; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.node_choices (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    node_id uuid NOT NULL,
    text text NOT NULL,
    next_node_id uuid,
    affection_delta integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.node_choices OWNER TO isekai;

--
-- Name: nodes; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.nodes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    route_id uuid NOT NULL,
    parent_id uuid,
    node_type character varying(20) NOT NULL,
    content json NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.nodes OWNER TO isekai;

--
-- Name: oauth_accounts; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.oauth_accounts (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    provider character varying(50) NOT NULL,
    provider_user_id character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.oauth_accounts OWNER TO isekai;

--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.password_resets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    token character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.password_resets OWNER TO isekai;

--
-- Name: posts; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.posts (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    image_urls text,
    like_count integer DEFAULT 0,
    comment_count integer DEFAULT 0,
    is_deleted boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.posts OWNER TO isekai;

--
-- Name: purchases; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.purchases (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    item_id character varying(100) NOT NULL,
    item_name character varying(255) NOT NULL,
    price numeric(10,2) NOT NULL,
    currency character varying(3),
    is_mock boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.purchases OWNER TO isekai;

--
-- Name: routes; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.routes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    script_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.routes OWNER TO isekai;

--
-- Name: scenes; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.scenes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    script_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    background_url text,
    bgm_url text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.scenes OWNER TO isekai;

--
-- Name: scripts; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.scripts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    slug character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    genre character varying(50) NOT NULL,
    cover_image_url text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.scripts OWNER TO isekai;

--
-- Name: share_cards; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.share_cards (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    share_type character varying(50) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    image_url text,
    extra_data jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.share_cards OWNER TO isekai;

--
-- Name: streak_records; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.streak_records (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    current_streak integer,
    max_streak integer,
    last_checkin_date date,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.streak_records OWNER TO isekai;

--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.subscriptions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    plan_id character varying(50) NOT NULL,
    status character varying(20),
    billing_cycle character varying(10),
    currency character varying(3),
    price numeric(10,2) NOT NULL,
    is_mock boolean,
    started_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone,
    cancelled_at timestamp with time zone
);


ALTER TABLE public.subscriptions OWNER TO isekai;

--
-- Name: unlocked_cgs; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.unlocked_cgs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    cg_id uuid NOT NULL,
    unlocked_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.unlocked_cgs OWNER TO isekai;

--
-- Name: unlocked_scripts; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.unlocked_scripts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    script_id uuid NOT NULL,
    unlocked_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.unlocked_scripts OWNER TO isekai;

--
-- Name: user_preferences; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.user_preferences (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    language character varying(10),
    bgm_enabled boolean,
    sfx_enabled boolean,
    text_speed character varying(20),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.user_preferences OWNER TO isekai;

--
-- Name: users; Type: TABLE; Schema: public; Owner: isekai
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255),
    display_name character varying(100),
    avatar_url text,
    email_verified boolean,
    oauth_provider character varying(50),
    oauth_id character varying(255),
    subscription_tier character varying(20),
    trial_started_at timestamp with time zone,
    trial_ends_at timestamp with time zone,
    onboarding_completed boolean,
    preferred_genre character varying(50),
    locale character varying(10),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO isekai;

--
-- Data for Name: achievements; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.achievements (id, user_id, achievement_id, title, description, icon_url, unlocked_at) FROM stdin;
4a882ee1-be4d-476b-8f25-9026698470b9	5c7d7fd6-5b64-420a-bc37-1cb72996b998	ach_001	初见	完成第一章	https://example.com/icon.png	2026-07-17 06:21:32.294309+00
\.


--
-- Data for Name: affection; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.affection (id, user_id, character_id, value, level, updated_at) FROM stdin;
c436bf52-8875-4f8c-8a31-d68849222ec5	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 08:50:04.934299+00
c400db49-a3ca-46ef-974a-598f23b98c74	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	22222222-2222-2222-2222-222222222222	0	acquaintance	2026-07-17 08:50:04.948362+00
94c2471d-9846-4c37-b1e9-b8b7a246aa67	198a83dc-6bba-4c2c-af10-90a8711f26d0	22222222-2222-2222-2222-222222222222	8	acquaintance	2026-07-17 03:55:13.676882+00
8409209d-a0d1-4980-a132-fbb3eb0dcec9	778dfb6a-46f5-415d-a114-35173f8d8893	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 09:03:54.316733+00
b2434af9-ce64-4bba-a201-3aecf63782a0	3da05a2a-43ba-424a-8f97-fb2256804474	22222222-2222-2222-2222-222222222222	8	acquaintance	2026-07-17 03:57:42.083753+00
1ec7c926-6777-4cba-9411-2286a37840cb	778dfb6a-46f5-415d-a114-35173f8d8893	22222222-2222-2222-2222-222222222222	0	acquaintance	2026-07-17 09:03:54.332389+00
2897b383-7d2e-4198-b9b6-ceda5c3ba9a0	5bcd3ab0-458d-4e0c-856a-5436b8c78662	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 09:08:49.954944+00
42dd16a6-a4af-4b07-bdf9-d5434a9778a0	d474b2b6-0bdb-4b67-b76a-bee0783328a8	a2222222-2222-2222-2222-222222222222	8	acquaintance	2026-07-17 04:04:35.886747+00
eebb9e10-1e43-49fe-aecf-9004c8861d83	d474b2b6-0bdb-4b67-b76a-bee0783328a8	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 04:04:36.007138+00
37fb8c6e-de07-410d-ada1-3a0181645a8e	1697729c-6110-45f9-b44c-0811949f0fb7	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 09:08:50.475312+00
54fa751a-ad65-4a64-b417-baa73664819a	8c9beb2b-5c24-4de2-bf56-433271037507	77777777-7777-7777-7777-777777777777	8	acquaintance	2026-07-17 04:09:35.955625+00
ce5436a8-3b13-4065-bcc6-646b427a5841	085801f9-68eb-48c2-b54c-1107fea60336	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 09:10:05.473461+00
b2cfe4fa-dc75-4802-82a9-dad35fe406eb	c17290b0-dcea-42db-836a-937446784655	22222222-2222-2222-2222-222222222222	8	acquaintance	2026-07-17 04:38:20.990541+00
0888108c-6206-45e5-b0e3-9893eb34508c	6f583b94-a4f6-47e4-a611-bd9ca902eb0a	77777777-7777-7777-7777-777777777777	6	acquaintance	2026-07-17 05:10:08.802091+00
7544cdc0-c8ca-4711-b743-e10f60c4e5fb	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	22222222-2222-2222-2222-222222222222	6	acquaintance	2026-07-17 05:13:46.003156+00
65564d51-5b15-499b-8ced-953844b2cebe	a2ba87f5-51a8-40c7-b84e-d46a48332cf4	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 09:10:15.833677+00
a39a9147-ef98-4e60-9bea-52953dbb0641	5cf0d44b-4b01-4f27-9969-595adff606ad	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 05:29:17.00017+00
c3802abe-8179-4d65-b5b2-758892505d4d	71534de5-9bbb-4e62-8130-7b0488eb3faa	22222222-2222-2222-2222-222222222222	11	acquaintance	2026-07-17 05:45:19.893172+00
0399e37f-3518-4974-a7d7-1203bbe54ea3	71534de5-9bbb-4e62-8130-7b0488eb3faa	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 05:45:19.919177+00
7a9c812e-848a-452e-a010-c8f29cd9c0fe	71534de5-9bbb-4e62-8130-7b0488eb3faa	a2222222-2222-2222-2222-222222222222	3	acquaintance	2026-07-17 05:45:19.94578+00
f63bf37b-cdcb-441d-8475-b60518d7dd41	f175ddf9-86d2-4670-8a05-e6c31b18aea9	22222222-2222-2222-2222-222222222222	0	acquaintance	2026-07-17 05:47:48.821995+00
c6b496db-46fc-4a1e-8782-a1c5ccf43cf3	735b1c47-8e0b-4184-9423-483014ad595c	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 05:48:34.809183+00
f325d2fa-b072-4166-8577-27bc84e9aec2	3f5f6396-b061-4d34-82c2-fb6f43942033	22222222-2222-2222-2222-222222222222	0	acquaintance	2026-07-17 05:52:00.618637+00
552d74be-a69b-40fe-b14e-d985e6c11630	0af81174-e857-4e63-b114-6973568adb25	22222222-2222-2222-2222-222222222222	3	acquaintance	2026-07-17 06:10:09.275201+00
8de359af-2f05-486f-998b-30d980763c17	6ee18a17-7ca4-4f67-9a8e-c0f346212ad4	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 06:27:56.445145+00
c5b9ae85-3fc2-4209-837b-de2f8ae0b87f	2ae26db0-76cd-4d01-8033-8727a4c31dde	22222222-2222-2222-2222-222222222222	0	acquaintance	2026-07-17 06:34:10.86888+00
8abb4d80-2b38-4ac0-825b-d21715e3b433	f7533307-789c-4884-b67e-90f1dd184a74	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 06:45:55.869526+00
bf4b4761-f4e2-4921-836c-4a63d6b5bc09	4c4df553-0ff6-4cbd-b294-12e24cefa68a	22222222-2222-2222-2222-222222222222	3	acquaintance	2026-07-17 07:14:06.111983+00
ef568445-59c4-4e13-a0de-9c7a92008059	ec6ecb8e-4be5-4ebb-99ea-a1c4e88baf59	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 07:14:27.068517+00
3aa607c4-2b55-49c5-9fa1-ce2565077bda	52bc08a5-62a3-4583-8089-f130935b3e5b	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 07:25:09.087541+00
a0aa0734-63f3-4b46-bf3b-d9a11bfcbd05	c5c5379c-ee36-4cbd-8437-b5041c865a8b	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 07:29:01.393841+00
6cbe95f9-5570-423d-a8ba-ad8ef49fde42	b7b5ec03-2bcc-4645-9754-bda06a954133	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 08:28:39.318851+00
ddcaafee-1a59-4ef1-af29-f4d082850a7c	4cde0b80-2b46-4081-b6af-8e70be92e8e7	77777777-7777-7777-7777-777777777777	3	acquaintance	2026-07-17 08:49:15.797965+00
694da165-e618-4b38-a5e5-f160c83aec96	4cde0b80-2b46-4081-b6af-8e70be92e8e7	22222222-2222-2222-2222-222222222222	0	acquaintance	2026-07-17 08:49:15.812499+00
\.


--
-- Data for Name: affection_history; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.affection_history (id, user_id, character_id, delta, old_value, new_value, old_level, new_level, reason, source_session_id, source_choice_id, created_at) FROM stdin;
46c62f11-ad8c-4e59-8154-d9922dfadd98	6f583b94-a4f6-47e4-a611-bd9ca902eb0a	77777777-7777-7777-7777-777777777777	3	3	6	acquaintance	acquaintance	choice	\N	\N	2026-07-17 05:10:08.804118+00
5f51a638-40f1-45c3-993f-15d1415b2486	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	22222222-2222-2222-2222-222222222222	3	3	6	acquaintance	acquaintance	choice	\N	\N	2026-07-17 05:13:46.004164+00
c54212df-9332-42de-8434-b632a90d9062	71534de5-9bbb-4e62-8130-7b0488eb3faa	22222222-2222-2222-2222-222222222222	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 05:17:02.276373+00
184eefe5-5e63-4c59-939e-30c1b3e253da	71534de5-9bbb-4e62-8130-7b0488eb3faa	22222222-2222-2222-2222-222222222222	5	3	8	acquaintance	acquaintance	choice	\N	\N	2026-07-17 05:17:02.296206+00
234039ca-1ab6-41f7-ad70-43487514ec0d	5cf0d44b-4b01-4f27-9969-595adff606ad	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 05:29:17.001301+00
346f7e0a-b83e-406f-b667-b70580c09bfc	71534de5-9bbb-4e62-8130-7b0488eb3faa	22222222-2222-2222-2222-222222222222	3	8	11	acquaintance	acquaintance	choice	\N	\N	2026-07-17 05:45:19.893911+00
333c3b42-183d-486c-9673-5a906412d57d	71534de5-9bbb-4e62-8130-7b0488eb3faa	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 05:45:19.919809+00
1a29e552-73ad-4c63-a5c6-0495cb5f5522	71534de5-9bbb-4e62-8130-7b0488eb3faa	a2222222-2222-2222-2222-222222222222	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 05:45:19.946416+00
0141fca2-e015-433e-8ec6-09f288b11415	735b1c47-8e0b-4184-9423-483014ad595c	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 05:48:34.810436+00
08594392-0e71-45e3-8557-eeba7e1111f0	0af81174-e857-4e63-b114-6973568adb25	22222222-2222-2222-2222-222222222222	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 06:10:09.276633+00
d4e02b1c-2439-4b55-84c1-e35a49f72032	6ee18a17-7ca4-4f67-9a8e-c0f346212ad4	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 06:27:56.447052+00
5f37a978-a4ec-4293-a6fc-0a6715af26b8	f7533307-789c-4884-b67e-90f1dd184a74	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 06:45:55.871047+00
ec0c51e6-dcba-4992-adb1-b5b69b0970a8	4c4df553-0ff6-4cbd-b294-12e24cefa68a	22222222-2222-2222-2222-222222222222	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 07:14:06.113866+00
53115ac7-0704-4bb2-8e04-d9572f93415c	ec6ecb8e-4be5-4ebb-99ea-a1c4e88baf59	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 07:14:27.069641+00
ecf7d729-9aae-40e4-8aae-8c7748808815	52bc08a5-62a3-4583-8089-f130935b3e5b	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 07:25:09.088412+00
9f4a9ca9-f106-4ffa-93ef-446aea15a294	c5c5379c-ee36-4cbd-8437-b5041c865a8b	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 07:29:01.394578+00
6bfff2b0-b8b4-44bf-8761-82382afd112a	b7b5ec03-2bcc-4645-9754-bda06a954133	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 08:28:39.319965+00
c5ef6533-2b9a-4dfd-8de3-d06b28956edf	4cde0b80-2b46-4081-b6af-8e70be92e8e7	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 08:49:15.798709+00
a48c7f22-8f03-4830-a43f-aa5d304e8973	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 08:50:04.93496+00
032ce5fb-139d-4450-a96d-3c666c5bde6a	778dfb6a-46f5-415d-a114-35173f8d8893	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 09:03:54.317505+00
aa1c1a49-b747-4afe-b6a1-197f56733573	5bcd3ab0-458d-4e0c-856a-5436b8c78662	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 09:08:49.955766+00
c9d63156-2f19-4a1a-8d98-576f735c78f1	1697729c-6110-45f9-b44c-0811949f0fb7	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 09:08:50.477044+00
2bd71a73-7515-4648-a27a-68dfea5a8226	085801f9-68eb-48c2-b54c-1107fea60336	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 09:10:05.474297+00
9e083cc9-b8de-462a-bf03-0744d4ffaec6	a2ba87f5-51a8-40c7-b84e-d46a48332cf4	77777777-7777-7777-7777-777777777777	3	0	3	acquaintance	acquaintance	choice	\N	\N	2026-07-17 09:10:15.834355+00
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.alembic_version (version_num) FROM stdin;
001
\.


--
-- Data for Name: cg_assets; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.cg_assets (id, script_id, route_id, name, image_url, created_at) FROM stdin;
\.


--
-- Data for Name: character_memories; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.character_memories (id, user_id, character_id, memory_text, embedding, source_session_id, confidence, is_compressed, created_at, updated_at, source) FROM stdin;
a82a94d0-42c2-42fa-a4f4-b72e65477b3f	6f583b94-a4f6-47e4-a611-bd9ca902eb0a	77777777-7777-7777-7777-777777777777	玩家选择了解星空，表现出对天文学的好奇心	\N	4fc54dce-9b6f-405d-b3cc-80426a3d4619	1.00	f	2026-07-17 05:05:43.651718+00	2026-07-17 05:05:43.651722+00	game_event
41c9da08-6102-4e58-9290-a9ad60e6bdcf	6f583b94-a4f6-47e4-a611-bd9ca902eb0a	77777777-7777-7777-7777-777777777777	玩家选择了解星空，表现出对天文学的好奇心	\N	4fc54dce-9b6f-405d-b3cc-80426a3d4619	1.00	f	2026-07-17 05:07:28.292518+00	2026-07-17 05:07:28.292523+00	game_event
e0a2a0f8-8d20-4af4-8009-3a63dd3f29b3	6f583b94-a4f6-47e4-a611-bd9ca902eb0a	\N	沈星澜提到月相与潮汐的关系，玩家表现出浓厚兴趣	\N	4fc54dce-9b6f-405d-b3cc-80426a3d4619	1.00	f	2026-07-17 05:07:28.320853+00	2026-07-17 05:07:28.320855+00	dialogue
5c808bb1-c26e-4732-9681-d4074279a729	2ae26db0-76cd-4d01-8033-8727a4c31dde	\N	test memory	\N	665c2291-0949-41e3-841e-8f43807380f7	1.00	f	2026-07-17 06:34:10.920465+00	2026-07-17 06:34:10.920469+00	game_event
\.


--
-- Data for Name: character_sprites; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.character_sprites (id, character_id, emotion, image_url, created_at) FROM stdin;
\.


--
-- Data for Name: characters; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.characters (id, script_id, name, description, dialogue_style, created_at) FROM stdin;
22222222-2222-2222-2222-222222222222	11111111-1111-1111-1111-111111111111	林辰	温柔的占星师，擅长解读星象。性格温和体贴，偶尔带点神秘感。相信命运和缘分，对每个人都充满善意。	gentle	2026-07-17 03:53:52.054288+00
a2222222-2222-2222-2222-222222222222	a1111111-1111-1111-1111-111111111111	藤原雪	大学文学教授，专攻古典日本文学。性格温和儒雅，擅长用诗歌表达情感。相信文字能传递心意，每个季节都有独特的美。	gentle	2026-07-17 04:03:48.53554+00
77777777-7777-7777-7777-777777777777	66666666-6666-6666-6666-666666666666	沈星澜	天才天文学家，专注于研究月相与潮汐的关系。外表冷峻，内心却有着不为人知的温柔。相信科学能解释一切，包括缘分。	mysterious	2026-07-17 04:03:50.122613+00
\.


--
-- Data for Name: collections; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.collections (id, user_id, item_type, item_id, item_name, image_url, unlocked_at) FROM stdin;
5a28a699-5acd-4bde-a02f-840c037f7c79	5c7d7fd6-5b64-420a-bc37-1cb72996b998	character	char_001	林月	https://example.com/char.png	2026-07-17 06:21:32.281391+00
\.


--
-- Data for Name: comments; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.comments (id, post_id, user_id, content, is_deleted, created_at) FROM stdin;
458fc124-69cd-4940-9245-7d7d0c4cb6b6	f43d176a-6726-4045-8e64-e8e2698f5e47	fbc9e9fd-e41f-4c25-9ebe-bd48d894807f	这是第一条评论	f	2026-07-17 06:16:11.670533+00
6329cd1c-54e4-4cf3-99b0-a4f0d665198a	4777d9b9-5e9b-4142-8ea7-c1a1ac7bc6af	8ddc774b-6361-468d-9f3f-b32553bd0efe	Nice!	f	2026-07-17 07:09:38.036907+00
7908c179-ccdd-47a1-b2d1-756a5fdc8655	974c9bba-5a8f-46a0-9564-47653bf1a7e0	cfcfa1c1-66b5-4334-97b5-c626091beb34	Nice!	f	2026-07-17 07:13:17.94147+00
\.


--
-- Data for Name: daily_checkins; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.daily_checkins (id, user_id, date, created_at) FROM stdin;
fbb453d4-43f1-49e9-8078-08fb0a0221a1	c4444a36-cfdb-4be6-ae51-25df8e615865	2026-07-17	2026-07-17 03:02:01.265843+00
355f40d5-5cc5-44ab-8fd5-4e9d4788982f	3da05a2a-43ba-424a-8f97-fb2256804474	2026-07-17	2026-07-17 03:46:09.28022+00
3daa282e-33f2-4101-a993-628965e9de42	c17290b0-dcea-42db-836a-937446784655	2026-07-17	2026-07-17 04:37:55.257196+00
5e862359-60ac-482c-97e2-85cd27006f1a	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	2026-07-17	2026-07-17 05:02:38.344928+00
02aaedd9-33a1-4ed5-8b9e-cf9f64fc300a	71534de5-9bbb-4e62-8130-7b0488eb3faa	2026-07-17	2026-07-17 05:17:02.31112+00
c6264dfa-1a01-4334-baa4-3f21768d17e0	2ae26db0-76cd-4d01-8033-8727a4c31dde	2026-07-17	2026-07-17 06:34:10.891685+00
2569e31a-04bc-4ac1-9e54-fccc1b45d02f	4c4df553-0ff6-4cbd-b294-12e24cefa68a	2026-07-17	2026-07-17 06:48:03.001419+00
eb555d66-9a9d-48c2-84fd-03c9d3d1472c	8ddc774b-6361-468d-9f3f-b32553bd0efe	2026-07-17	2026-07-17 07:09:37.885042+00
8899374a-6657-4a20-8b0e-35f594339a4d	cfcfa1c1-66b5-4334-97b5-c626091beb34	2026-07-17	2026-07-17 07:13:17.801086+00
53d7e088-71cd-44f0-bbad-97df80349b99	4cde0b80-2b46-4081-b6af-8e70be92e8e7	2026-07-18	2026-07-17 08:49:15.820425+00
7bafe7b7-f003-4325-9eb3-b67d099fc6c5	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	2026-07-18	2026-07-17 08:50:04.954763+00
255af64f-0aa0-4d46-8b59-92264d32c2a9	778dfb6a-46f5-415d-a114-35173f8d8893	2026-07-18	2026-07-17 09:03:54.338297+00
69b4ac5f-4641-496c-b610-c60df76c2343	3e9b3ff7-ccbf-47ba-99ef-1a890bd513c7	2026-07-18	2026-07-17 09:06:08.672591+00
1079efd0-1a6f-4074-af92-64976357985a	5bcd3ab0-458d-4e0c-856a-5436b8c78662	2026-07-18	2026-07-17 09:08:56.515858+00
487f9713-6b6f-4483-88ca-f12231afcc6b	1697729c-6110-45f9-b44c-0811949f0fb7	2026-07-18	2026-07-17 09:08:57.151349+00
7d8f209c-dde3-4949-94a5-adc655250f4c	a2ba87f5-51a8-40c7-b84e-d46a48332cf4	2026-07-18	2026-07-17 09:10:21.728699+00
\.


--
-- Data for Name: daily_tasks; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.daily_tasks (id, user_id, date, task_type, progress, target, completed, claimed, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: email_verifications; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.email_verifications (id, user_id, token, expires_at, used, created_at) FROM stdin;
\.


--
-- Data for Name: fragment_transactions; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.fragment_transactions (id, user_id, amount, reason, created_at) FROM stdin;
7141a028-aae2-4b99-907a-9abd3e791893	f016da07-7326-4763-a309-c471722195ab	100	purchase:fragments_100	2026-07-17 06:13:22.515668+00
096c493c-d1c1-4311-bcb7-62c17099d6c2	ecfc3e91-fb50-4985-b8c4-55c479d6e8b6	100	recharge:mock	2026-07-17 06:32:20.371622+00
fe606494-d885-4335-bc49-6fcf5795eede	27620270-1362-460a-b84a-defc09135cb8	100	recharge:mock	2026-07-17 06:33:05.225768+00
dc42bcfd-b4c1-4e45-9ae4-ce58dff3b286	2ae26db0-76cd-4d01-8033-8727a4c31dde	100	recharge:mock	2026-07-17 06:34:11.00071+00
c792b8b6-6bba-4f67-9f99-a8f666078107	4c4df553-0ff6-4cbd-b294-12e24cefa68a	100	recharge:mock	2026-07-17 06:48:03.215321+00
fa232683-50eb-47d8-9a7a-c33d35ae629a	8ddc774b-6361-468d-9f3f-b32553bd0efe	100	recharge:mock	2026-07-17 07:09:38.007171+00
54555325-63fb-47d4-8496-e672bb8ebf67	cfcfa1c1-66b5-4334-97b5-c626091beb34	100	recharge:mock	2026-07-17 07:13:17.908699+00
b9d62a07-8889-4a3d-bb55-a5c0070f2866	4cde0b80-2b46-4081-b6af-8e70be92e8e7	100	recharge:mock	2026-07-17 08:49:15.845358+00
63aead0e-30c1-4178-b007-1aa8fa0a07eb	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	100	recharge:mock	2026-07-17 08:50:04.978046+00
1cfedabc-bde8-409a-b848-89245389cf54	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	100	purchase:fragments_100	2026-07-17 08:50:04.986948+00
786598e2-61e3-4fe6-bdd4-cb5b07b3f550	778dfb6a-46f5-415d-a114-35173f8d8893	100	recharge:mock	2026-07-17 09:03:54.360496+00
decf5edf-c919-4b82-99fa-65df6468c560	778dfb6a-46f5-415d-a114-35173f8d8893	100	purchase:fragments_100	2026-07-17 09:03:54.369133+00
eb4c05b9-9798-4c5d-acdd-a6498486ac15	3e9b3ff7-ccbf-47ba-99ef-1a890bd513c7	100	purchase:fragments_100	2026-07-17 09:07:44.866282+00
\.


--
-- Data for Name: fragments; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.fragments (id, user_id, balance, updated_at) FROM stdin;
cf85762a-b19d-42bb-83d7-8dcd293b55d2	f016da07-7326-4763-a309-c471722195ab	100	2026-07-17 06:13:22.514503+00
0be404d6-ccf9-49ba-81d2-618e68822854	ecfc3e91-fb50-4985-b8c4-55c479d6e8b6	100	2026-07-17 06:32:20.370515+00
2c42978b-8d6a-4dab-b77f-fa78e67ee230	27620270-1362-460a-b84a-defc09135cb8	100	2026-07-17 06:33:05.225247+00
56c7b0ab-8e6e-4221-b18b-fe9940474fd7	2ae26db0-76cd-4d01-8033-8727a4c31dde	100	2026-07-17 06:34:10.99994+00
9d421d5e-895c-4dc0-a26d-52d77f23ef7c	4c4df553-0ff6-4cbd-b294-12e24cefa68a	100	2026-07-17 06:48:03.213736+00
c095eb39-07c4-41e2-a0d0-67326dec7845	8ddc774b-6361-468d-9f3f-b32553bd0efe	100	2026-07-17 07:09:38.005588+00
d2af7f2e-fc0a-4a9f-8e26-a67a5b10a593	cfcfa1c1-66b5-4334-97b5-c626091beb34	100	2026-07-17 07:13:17.907361+00
c82e11d6-5a67-4bed-a14d-2f512a663167	4cde0b80-2b46-4081-b6af-8e70be92e8e7	100	2026-07-17 08:49:15.8445+00
b0ca4bed-0279-40f3-aed8-701c44d111a0	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	200	2026-07-17 08:50:04.986289+00
7832ea89-7290-4079-b14a-7081c8550a7f	778dfb6a-46f5-415d-a114-35173f8d8893	200	2026-07-17 09:03:54.368581+00
604b0c57-2294-4b5a-a86b-9574ee49d91d	3e9b3ff7-ccbf-47ba-99ef-1a890bd513c7	100	2026-07-17 09:07:44.865563+00
\.


--
-- Data for Name: game_progress; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.game_progress (id, session_id, node_id, choice_id, created_at) FROM stdin;
c05fdc39-c5c0-4c60-be08-46b7e143b95c	f9990a53-606f-4461-a3e6-41aae2b95152	44444444-4444-4444-4444-444444444441	55555555-5555-5555-5555-555555555551	2026-07-17 03:55:13.556741+00
50832bc6-d82f-4768-b81f-56790beb70c9	f9990a53-606f-4461-a3e6-41aae2b95152	44444444-4444-4444-4444-444444444443	55555555-5555-5555-5555-555555555553	2026-07-17 03:55:13.682086+00
13c0d6dd-f517-4fb0-8703-634e0ed5be84	4f93429d-6264-4ee7-bf53-5b9bd3b45b12	44444444-4444-4444-4444-444444444441	55555555-5555-5555-5555-555555555551	2026-07-17 03:57:14.534415+00
f052d95f-f436-4dff-972a-768ef2ee290c	4f93429d-6264-4ee7-bf53-5b9bd3b45b12	44444444-4444-4444-4444-444444444443	55555555-5555-5555-5555-555555555553	2026-07-17 03:57:42.08877+00
25500344-96d5-4d2a-b327-8642ebf6c635	9ef07a7a-f93f-4e4e-92b2-261c904799f6	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 04:04:35.646985+00
4d7ed615-b418-4717-ae5b-8416438cb366	9ef07a7a-f93f-4e4e-92b2-261c904799f6	99999999-9999-9999-9999-999999999992	cccccccc-cccc-cccc-cccc-cccccccccccc	2026-07-17 04:04:35.694693+00
f3c03332-bf08-4cde-95ee-eacba3860430	084ee0f0-e154-420a-b0c5-5875b4cedca8	a4444444-4444-4444-4444-444444444441	a5555555-5555-5555-5555-555555555551	2026-07-17 04:04:35.846773+00
e4e9c0e6-61f2-423e-ab07-7663a77620f1	084ee0f0-e154-420a-b0c5-5875b4cedca8	a4444444-4444-4444-4444-444444444442	a5555555-5555-5555-5555-555555555553	2026-07-17 04:04:35.891294+00
5642a79b-492d-443e-bf63-f75924a4ea2a	ba5c132e-2cff-454b-8961-1c9eaae406aa	99999999-9999-9999-9999-999999999991	bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb	2026-07-17 04:04:35.995105+00
674c9313-ab1d-4563-a162-a95f007bdf97	ba5c132e-2cff-454b-8961-1c9eaae406aa	99999999-9999-9999-9999-999999999993	ffffffff-ffff-ffff-ffff-ffffffffffff	2026-07-17 04:04:36.011861+00
ddcd253f-6060-4eb3-8001-83c9218b49ee	53e984e0-15f4-4492-8e00-48c7ddb8e500	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 04:09:35.938904+00
5e942d43-9c85-482a-8855-99f1137802aa	53e984e0-15f4-4492-8e00-48c7ddb8e500	99999999-9999-9999-9999-999999999992	cccccccc-cccc-cccc-cccc-cccccccccccc	2026-07-17 04:09:35.960669+00
c74bf656-faac-4499-ae43-acee37e639f0	4fc54dce-9b6f-405d-b3cc-80426a3d4619	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 04:37:18.954324+00
f3f06206-7ab9-4389-bcb2-a96f02f5261a	7d593324-ad85-438f-b123-22656d47a921	44444444-4444-4444-4444-444444444441	55555555-5555-5555-5555-555555555551	2026-07-17 04:38:20.905614+00
532405c7-5a0b-4744-9e52-edd081e1bcda	7d593324-ad85-438f-b123-22656d47a921	44444444-4444-4444-4444-444444444443	55555555-5555-5555-5555-555555555553	2026-07-17 04:38:20.996129+00
b74a9dde-d1ad-42bd-a5b3-3491cbecef28	5e631615-d121-4c71-b944-4f700910dbbd	44444444-4444-4444-4444-444444444441	55555555-5555-5555-5555-555555555551	2026-07-17 05:04:09.56113+00
d36c8420-0968-4ad9-8ed1-a92d1782c453	25d62630-4a1a-4164-ae2f-69e6f12f1545	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 05:10:08.812599+00
6a80e4f9-8ee1-46a8-b49a-2a8c40676873	f30ae73d-8e7e-4761-97cc-7dacc8d801c3	44444444-4444-4444-4444-444444444441	55555555-5555-5555-5555-555555555551	2026-07-17 05:13:46.01162+00
883c38c1-d63a-4a73-a4a8-8a2dae30a5c3	31b6d998-419e-46f8-ab61-93ff7ce9a380	44444444-4444-4444-4444-444444444441	55555555-5555-5555-5555-555555555551	2026-07-17 05:17:02.282072+00
272a1807-16a0-4442-be1d-233a800139a2	31b6d998-419e-46f8-ab61-93ff7ce9a380	44444444-4444-4444-4444-444444444443	55555555-5555-5555-5555-555555555553	2026-07-17 05:17:02.301671+00
e314d2ec-5e80-45af-b523-0a085ce5aecb	8080c48a-346c-47b0-9cff-f64bc324034c	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 05:29:17.007894+00
4b00e49d-c894-4c71-981a-e1a89801b5f0	a322fd30-9c0a-4ea2-9898-abf24253f2fa	44444444-4444-4444-4444-444444444441	55555555-5555-5555-5555-555555555551	2026-07-17 05:45:19.899098+00
14f29362-5823-4142-b82e-6c349b9baf44	f86552a6-5e6b-4d29-b5de-30bc8861492c	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 05:45:19.924396+00
d0f68a89-33d1-4f18-aaa7-937f398655e9	0fc828de-1b66-4b9f-ab58-f88166e4298a	a4444444-4444-4444-4444-444444444441	a5555555-5555-5555-5555-555555555551	2026-07-17 05:45:19.951315+00
c4479a93-26fe-49e6-8d3e-f3b2b0f61f6a	bded6e9e-bbc7-49b5-a6bf-795248e3c55c	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 05:48:34.817729+00
cb54d1c1-1081-4fb4-9683-e59dd621ad9d	a8da4455-656c-49b4-985f-d03f7384b543	44444444-4444-4444-4444-444444444441	55555555-5555-5555-5555-555555555551	2026-07-17 06:10:09.285167+00
88ca2418-1e01-4ac0-bf2d-245c0e32792e	cc4ef05c-4076-41a8-8da9-cd47a2a2d78b	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 06:27:56.454938+00
330b5027-0eda-47b8-aa73-de4752574ff4	e7b7eb7f-86d6-4aa8-b15c-07bfdfebc732	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 06:45:55.879586+00
1cf38f00-d5d1-4ed8-afc9-f061f7b9ee60	a21ffead-33ea-4f04-954a-d106c5f56d8d	44444444-4444-4444-4444-444444444441	55555555-5555-5555-5555-555555555551	2026-07-17 07:14:06.121327+00
d6e9c80f-cb46-44c3-9738-3104204ec7ef	8bede954-9d80-47c6-af15-3c832dbd50e0	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 07:14:27.076393+00
d80afa67-aba9-4ad6-be28-58322416d7b8	3786d7d1-065e-45ae-919d-c1590e758096	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 07:25:09.094249+00
c1773a56-26d4-4c2c-a66e-0c1ae28b7991	1d1a935b-2881-4a93-bbba-003196af38cb	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 07:29:01.402221+00
e539e411-7c65-4819-b5b6-48b7f91c8758	8b04cb87-d7b6-43d5-9745-86579e3707c1	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 08:28:39.326929+00
aee4786a-c228-42d1-864e-527ed9aed6dd	878945e1-7881-4556-9afc-36fb2da387a1	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 08:49:15.803692+00
044ba051-8b22-422e-b8c3-7f33ab187b1a	0a0f46f9-9837-46eb-a54b-4cc44d183383	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 08:50:04.940003+00
31de4b88-5704-4401-b260-86dc4fdab31b	a4c8205f-5b94-468c-9fd9-8afd9a775a20	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 09:03:54.322721+00
42364373-53f8-4eb8-932a-b0c36533635d	ea90a8b2-249b-4621-b858-9a8ff5c06fd0	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 09:08:49.962478+00
873d2fe4-b1e5-4339-b534-797970f25d16	cde6c5c9-5122-4c47-8cc0-5ca32b5087f9	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 09:08:50.483512+00
14520495-561d-40db-b6fc-d648902c75b6	f95101e3-0be3-444b-83ef-17856c1c4d89	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 09:10:05.480774+00
f1376044-bd8c-4ebe-9ebb-fc39d52db754	64155bb4-ac91-4a90-9263-8cd89f0cd303	99999999-9999-9999-9999-999999999991	aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	2026-07-17 09:10:15.840727+00
\.


--
-- Data for Name: game_sessions; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.game_sessions (id, user_id, script_id, route_id, current_node_id, status, custom_name, avatar_choice, started_at, completed_at, ending_type, choice_history, metadata) FROM stdin;
e7b7eb7f-86d6-4aa8-b15c-07bfdfebc732	f7533307-789c-4884-b67e-90f1dd184a74	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 06:45:53.006012+00	\N	\N	[]	{}
f9990a53-606f-4461-a3e6-41aae2b95152	198a83dc-6bba-4c2c-af10-90a8711f26d0	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444447	completed	\N	\N	2026-07-17 03:55:13.449418+00	2026-07-17 03:55:13.681915+00	good	[]	{}
af93eea7-09f9-4d97-ac44-b2685e23efa0	4c4df553-0ff6-4cbd-b294-12e24cefa68a	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 06:48:02.953297+00	\N	\N	[]	{}
4f93429d-6264-4ee7-bf53-5b9bd3b45b12	3da05a2a-43ba-424a-8f97-fb2256804474	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444447	completed	\N	\N	2026-07-17 03:57:14.515254+00	2026-07-17 03:57:42.088616+00	good	[]	{}
489489fd-1b7a-44f4-97ad-f6aaf68f9e2e	8ddc774b-6361-468d-9f3f-b32553bd0efe	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999991	active	\N	\N	2026-07-17 07:09:37.859804+00	\N	\N	[]	{}
9ef07a7a-f93f-4e4e-92b2-261c904799f6	d474b2b6-0bdb-4b67-b76a-bee0783328a8	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999994	completed	\N	\N	2026-07-17 04:04:35.556639+00	2026-07-17 04:04:35.694539+00	good	[]	{}
505c342a-9efc-43a5-8090-8031c7319204	4c4df553-0ff6-4cbd-b294-12e24cefa68a	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 07:09:50.628004+00	\N	\N	[]	{}
084ee0f0-e154-420a-b0c5-5875b4cedca8	d474b2b6-0bdb-4b67-b76a-bee0783328a8	a1111111-1111-1111-1111-111111111111	a3333333-3333-3333-3333-333333333333	a4444444-4444-4444-4444-444444444444	completed	\N	\N	2026-07-17 04:04:35.760947+00	2026-07-17 04:04:35.891141+00	good	[]	{}
944f5a81-0860-4227-a5b5-c1c225704bea	4c4df553-0ff6-4cbd-b294-12e24cefa68a	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 07:12:28.068555+00	\N	\N	[]	{}
ba5c132e-2cff-454b-8961-1c9eaae406aa	d474b2b6-0bdb-4b67-b76a-bee0783328a8	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999996	completed	\N	\N	2026-07-17 04:04:35.957397+00	2026-07-17 04:04:36.011717+00	bad	[]	{}
acd94031-2301-4c25-8098-bec4d9311662	cfcfa1c1-66b5-4334-97b5-c626091beb34	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999991	active	\N	\N	2026-07-17 07:13:17.768403+00	\N	\N	[]	{}
53e984e0-15f4-4492-8e00-48c7ddb8e500	8c9beb2b-5c24-4de2-bf56-433271037507	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999994	completed	\N	\N	2026-07-17 04:09:35.906019+00	2026-07-17 04:09:35.960526+00	good	[]	{}
4fc54dce-9b6f-405d-b3cc-80426a3d4619	6f583b94-a4f6-47e4-a611-bd9ca902eb0a	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 04:37:18.815383+00	\N	\N	[]	{}
935d2eb8-0fa3-40f7-94a9-3474426cccf6	4c4df553-0ff6-4cbd-b294-12e24cefa68a	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 07:13:31.440872+00	\N	\N	[]	{}
7d593324-ad85-438f-b123-22656d47a921	c17290b0-dcea-42db-836a-937446784655	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444447	completed	\N	\N	2026-07-17 04:38:20.781268+00	2026-07-17 04:38:20.995944+00	good	[]	{}
5e631615-d121-4c71-b944-4f700910dbbd	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444443	active	\N	\N	2026-07-17 05:02:55.444981+00	\N	\N	[]	{}
25d62630-4a1a-4164-ae2f-69e6f12f1545	6f583b94-a4f6-47e4-a611-bd9ca902eb0a	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 05:10:08.727516+00	\N	\N	[]	{}
f30ae73d-8e7e-4761-97cc-7dacc8d801c3	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444443	active	\N	\N	2026-07-17 05:13:45.918769+00	\N	\N	[]	{}
31b6d998-419e-46f8-ab61-93ff7ce9a380	71534de5-9bbb-4e62-8130-7b0488eb3faa	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444447	completed	\N	\N	2026-07-17 05:17:02.259021+00	2026-07-17 05:17:02.301523+00	good	[]	{}
8080c48a-346c-47b0-9cff-f64bc324034c	5cf0d44b-4b01-4f27-9969-595adff606ad	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 05:29:14.204229+00	\N	\N	[]	{}
a322fd30-9c0a-4ea2-9898-abf24253f2fa	71534de5-9bbb-4e62-8130-7b0488eb3faa	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444443	active	\N	\N	2026-07-17 05:45:19.87836+00	\N	\N	[]	{}
f86552a6-5e6b-4d29-b5de-30bc8861492c	71534de5-9bbb-4e62-8130-7b0488eb3faa	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 05:45:19.904955+00	\N	\N	[]	{}
0fc828de-1b66-4b9f-ab58-f88166e4298a	71534de5-9bbb-4e62-8130-7b0488eb3faa	a1111111-1111-1111-1111-111111111111	a3333333-3333-3333-3333-333333333333	a4444444-4444-4444-4444-444444444442	active	\N	\N	2026-07-17 05:45:19.931533+00	\N	\N	[]	{}
402aaa99-3f87-467e-aa5e-d184b2690e79	f175ddf9-86d2-4670-8a05-e6c31b18aea9	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 05:47:48.672195+00	\N	\N	[]	{}
bded6e9e-bbc7-49b5-a6bf-795248e3c55c	735b1c47-8e0b-4184-9423-483014ad595c	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 05:48:32.028046+00	\N	\N	[]	{}
09b2b669-1523-433e-97b2-d7f9c4a4cc8e	3f5f6396-b061-4d34-82c2-fb6f43942033	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 05:52:00.581811+00	\N	\N	[]	{}
a8da4455-656c-49b4-985f-d03f7384b543	0af81174-e857-4e63-b114-6973568adb25	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444443	active	\N	\N	2026-07-17 06:10:09.252755+00	\N	\N	[]	{}
cc4ef05c-4076-41a8-8da9-cd47a2a2d78b	6ee18a17-7ca4-4f67-9a8e-c0f346212ad4	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 06:27:53.588446+00	\N	\N	[]	{}
5ecb3ad3-8a9b-4a52-adde-ef670a2a12c0	2ae26db0-76cd-4d01-8033-8727a4c31dde	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 06:34:10.728251+00	\N	\N	[]	{}
665c2291-0949-41e3-841e-8f43807380f7	2ae26db0-76cd-4d01-8033-8727a4c31dde	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 06:34:10.790677+00	\N	\N	[]	{}
a21ffead-33ea-4f04-954a-d106c5f56d8d	4c4df553-0ff6-4cbd-b294-12e24cefa68a	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444443	active	\N	\N	2026-07-17 07:14:06.094093+00	\N	\N	[]	{}
8bede954-9d80-47c6-af15-3c832dbd50e0	ec6ecb8e-4be5-4ebb-99ea-a1c4e88baf59	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 07:14:23.998596+00	\N	\N	[]	{}
3786d7d1-065e-45ae-919d-c1590e758096	52bc08a5-62a3-4583-8089-f130935b3e5b	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 07:25:06.009524+00	\N	\N	[]	{}
1d1a935b-2881-4a93-bbba-003196af38cb	c5c5379c-ee36-4cbd-8437-b5041c865a8b	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 07:28:58.302676+00	\N	\N	[]	{}
8b04cb87-d7b6-43d5-9745-86579e3707c1	b7b5ec03-2bcc-4645-9754-bda06a954133	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 08:28:36.291427+00	\N	\N	[]	{}
dd435b6e-3ee7-4d30-9648-ee9532b33653	14df719c-0d22-4032-bbac-ae65a6078c07	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999991	active	\N	\N	2026-07-17 08:38:46.085539+00	\N	\N	[]	{}
878945e1-7881-4556-9afc-36fb2da387a1	4cde0b80-2b46-4081-b6af-8e70be92e8e7	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 08:49:15.778368+00	\N	\N	[]	{}
0a0f46f9-9837-46eb-a54b-4cc44d183383	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 08:50:04.91549+00	\N	\N	[]	{}
a4c8205f-5b94-468c-9fd9-8afd9a775a20	778dfb6a-46f5-415d-a114-35173f8d8893	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 09:03:54.295909+00	\N	\N	[]	{}
a1ee681e-23e3-49ab-b140-24af8e5de762	d945e90f-6ab4-4c45-8280-9fc98824d923	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 09:04:22.495265+00	\N	\N	[]	{}
2d71f566-408c-471b-af78-ed0b14cd5e68	d945e90f-6ab4-4c45-8280-9fc98824d923	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 09:04:22.510545+00	\N	\N	[]	{}
1b3115e2-155d-4613-94d5-725c15d28882	d945e90f-6ab4-4c45-8280-9fc98824d923	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 09:04:22.524135+00	\N	\N	[]	{}
a6057f4f-856d-4649-b3e5-4c6e82b5a512	3e9b3ff7-ccbf-47ba-99ef-1a890bd513c7	11111111-1111-1111-1111-111111111111	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	active	\N	\N	2026-07-17 09:06:50.800134+00	\N	\N	[]	{}
ea90a8b2-249b-4621-b858-9a8ff5c06fd0	5bcd3ab0-458d-4e0c-856a-5436b8c78662	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 09:08:46.623245+00	\N	\N	[]	{}
cde6c5c9-5122-4c47-8cc0-5ca32b5087f9	1697729c-6110-45f9-b44c-0811949f0fb7	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 09:08:47.083464+00	\N	\N	[]	{}
f95101e3-0be3-444b-83ef-17856c1c4d89	085801f9-68eb-48c2-b54c-1107fea60336	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 09:10:02.402546+00	\N	\N	[]	{}
64155bb4-ac91-4a90-9263-8cd89f0cd303	a2ba87f5-51a8-40c7-b84e-d46a48332cf4	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	active	\N	\N	2026-07-17 09:10:12.651779+00	\N	\N	[]	{}
23a66d1e-fd95-47eb-81ed-f5ad58757453	60991d04-c6ad-425a-91f5-4c1001d6ad5c	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999991	active	\N	\N	2026-07-17 09:51:56.286623+00	\N	\N	[]	{}
4d346a30-d204-4740-8f9e-19fc2e53cb3d	fbb5e757-e3fc-43d6-b77e-6f87dc2ad300	66666666-6666-6666-6666-666666666666	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999991	active	\N	\N	2026-07-17 10:02:30.287163+00	\N	\N	[]	{}
\.


--
-- Data for Name: node_choices; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.node_choices (id, node_id, text, next_node_id, affection_delta, created_at) FROM stdin;
55555555-5555-5555-5555-555555555551	44444444-4444-4444-4444-444444444441	我也很喜欢星星！能告诉我更多关于星象的知识吗？	44444444-4444-4444-4444-444444444443	3	2026-07-17 03:53:52.059807+00
55555555-5555-5555-5555-555555555552	44444444-4444-4444-4444-444444444441	抱歉，我只是来喝咖啡的，不太懂星象。	44444444-4444-4444-4444-444444444444	-2	2026-07-17 03:53:52.05981+00
55555555-5555-5555-5555-555555555553	44444444-4444-4444-4444-444444444443	好啊！我很想看看我的星盘，什么时候方便？	44444444-4444-4444-4444-444444444447	5	2026-07-17 03:53:52.059811+00
55555555-5555-5555-5555-555555555554	44444444-4444-4444-4444-444444444443	谢谢你的邀请，不过我最近比较忙，可能没时间。	44444444-4444-4444-4444-444444444448	-1	2026-07-17 03:53:52.059811+00
55555555-5555-5555-5555-555555555555	44444444-4444-4444-4444-444444444444	好吧，那就一杯咖啡。不过我真的很忙。	44444444-4444-4444-4444-444444444448	2	2026-07-17 03:53:52.059812+00
55555555-5555-5555-5555-555555555556	44444444-4444-4444-4444-444444444444	不用了，谢谢。我先走了。	44444444-4444-4444-4444-444444444449	-3	2026-07-17 03:53:52.059813+00
a5555555-5555-5555-5555-555555555551	a4444444-4444-4444-4444-444444444441	我读过一些和歌，能给我讲讲樱花在文学中的意义吗？	a4444444-4444-4444-4444-444444444442	3	2026-07-17 04:03:48.541459+00
a5555555-5555-5555-5555-555555555552	a4444444-4444-4444-4444-444444444441	我对古典文学不太感兴趣，只是路过看看。	a4444444-4444-4444-4444-444444444443	-2	2026-07-17 04:03:48.541461+00
a5555555-5555-5555-5555-555555555553	a4444444-4444-4444-4444-444444444442	当然愿意！我对你的研究很感兴趣！	a4444444-4444-4444-4444-444444444444	5	2026-07-17 04:03:48.541462+00
a5555555-5555-5555-5555-555555555554	a4444444-4444-4444-4444-444444444442	谢谢，但我现在没时间，下次吧。	a4444444-4444-4444-4444-444444444445	-1	2026-07-17 04:03:48.541463+00
a5555555-5555-5555-5555-555555555555	a4444444-4444-4444-4444-444444444443	既然来了，就听你讲讲吧。	a4444444-4444-4444-4444-444444444445	2	2026-07-17 04:03:48.541464+00
a5555555-5555-5555-5555-555555555556	a4444444-4444-4444-4444-444444444443	不用了，我还有事。再见。	a4444444-4444-4444-4444-444444444446	-3	2026-07-17 04:03:48.541464+00
aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa	99999999-9999-9999-9999-999999999991	虽然不是爱好者，但我对星空很好奇！能给我讲讲月相吗？	99999999-9999-9999-9999-999999999992	3	2026-07-17 04:03:50.128771+00
bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb	99999999-9999-9999-9999-999999999991	我只是路过，对天文学没什么兴趣。	99999999-9999-9999-9999-999999999993	-2	2026-07-17 04:03:50.128775+00
cccccccc-cccc-cccc-cccc-cccccccccccc	99999999-9999-9999-9999-999999999992	我相信！科学与占星并不矛盾，我想了解更多！	99999999-9999-9999-9999-999999999994	5	2026-07-17 04:03:50.128776+00
dddddddd-dddd-dddd-dddd-dddddddddddd	99999999-9999-9999-9999-999999999992	我更喜欢脚踏实地，占星太玄乎了。	99999999-9999-9999-9999-999999999995	-1	2026-07-17 04:03:50.128778+00
eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee	99999999-9999-9999-9999-999999999993	既然来了，就听听你的研究吧。	99999999-9999-9999-9999-999999999995	2	2026-07-17 04:03:50.128779+00
ffffffff-ffff-ffff-ffff-ffffffffffff	99999999-9999-9999-9999-999999999993	不用了，我更喜欢安静地散步。再见。	99999999-9999-9999-9999-999999999996	-3	2026-07-17 04:03:50.12878+00
\.


--
-- Data for Name: nodes; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.nodes (id, route_id, parent_id, node_type, content, created_at) FROM stdin;
44444444-4444-4444-4444-444444444441	33333333-3333-3333-3333-333333333333	\N	preset	{"character": "\\u6797\\u8fb0", "character_id": "22222222-2222-2222-2222-222222222222", "text": "\\u4f60\\u597d\\uff0c\\u6211\\u662f\\u6797\\u8fb0\\u3002\\u4eca\\u665a\\u7684\\u661f\\u8c61\\u5f88\\u7f8e\\uff0c\\u730e\\u6237\\u5ea7\\u548c\\u5929\\u72fc\\u661f\\u5f62\\u6210\\u4e86\\u7f55\\u89c1\\u7684\\u89d2\\u5ea6...\\u554a\\uff0c\\u62b1\\u6b49\\uff0c\\u6211\\u662f\\u4e0d\\u662f\\u5413\\u5230\\u4f60\\u4e86\\uff1f\\u6211\\u53ea\\u662f\\u592a\\u559c\\u6b22\\u89c2\\u661f\\u4e86\\u3002\\u4f60\\u4e5f\\u662f\\u6765\\u770b\\u661f\\u661f\\u7684\\u5417\\uff1f", "emotion": "warm", "background": "cafe_night", "scene": "opening"}	2026-07-17 03:53:52.057577+00
44444444-4444-4444-4444-444444444443	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	preset	{"character": "\\u6797\\u8fb0", "character_id": "22222222-2222-2222-2222-222222222222", "text": "\\u771f\\u7684\\u5417\\uff1f\\u592a\\u597d\\u4e86\\uff01\\u4f60\\u4e5f\\u559c\\u6b22\\u661f\\u661f\\u554a\\u3002\\u4f60\\u77e5\\u9053\\u5417\\uff0c\\u5728\\u5360\\u661f\\u5b66\\u91cc\\uff0c\\u4e24\\u4e2a\\u4eba\\u7684\\u661f\\u76d8\\u5982\\u679c\\u5951\\u5408\\uff0c\\u5c31\\u4f1a\\u4ea7\\u751f\\u5947\\u5999\\u7684\\u5171\\u9e23\\u3002\\u6211\\u53ef\\u4ee5\\u5e2e\\u4f60\\u770b\\u770b\\u4f60\\u7684\\u661f\\u76d8...\\u5982\\u679c\\u4f60\\u613f\\u610f\\u7684\\u8bdd\\u3002", "emotion": "excited", "background": "cafe_night", "scene": "friendly_path"}	2026-07-17 03:53:52.057579+00
44444444-4444-4444-4444-444444444444	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444441	preset	{"character": "\\u6797\\u8fb0", "character_id": "22222222-2222-2222-2222-222222222222", "text": "\\u554a...\\u62b1\\u6b49\\uff0c\\u6211\\u592a\\u5510\\u7a81\\u4e86\\u3002\\u6211\\u53ea\\u662f...\\u6709\\u65f6\\u5019\\u4f1a\\u8fc7\\u4e8e\\u6c89\\u6d78\\u5728\\u81ea\\u5df1\\u7684\\u4e16\\u754c\\u91cc\\u3002\\u5982\\u679c\\u4f60\\u4e0d\\u4ecb\\u610f\\u7684\\u8bdd\\uff0c\\u6211\\u53ef\\u4ee5\\u8bf7\\u4f60\\u559d\\u676f\\u5496\\u5561\\u5f53\\u4f5c\\u8d54\\u793c\\u5417\\uff1f", "emotion": "apologetic", "background": "cafe_night", "scene": "cold_path"}	2026-07-17 03:53:52.05758+00
44444444-4444-4444-4444-444444444447	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444443	ending	{"character": "\\u6797\\u8fb0", "character_id": "22222222-2222-2222-2222-222222222222", "text": "\\u592a\\u597d\\u4e86\\uff01\\u90a3\\u6211\\u4eec\\u7ea6\\u597d\\u4e86\\uff0c\\u660e\\u665a\\u5929\\u6587\\u9986\\u89c1\\u3002\\u6211\\u4f1a\\u4e3a\\u4f60\\u51c6\\u5907\\u4e00\\u4efd\\u7279\\u522b\\u7684\\u661f\\u76d8\\u89e3\\u8bfb...\\u4e5f\\u8bb8\\uff0c\\u8fd9\\u4f1a\\u662f\\u6211\\u4eec\\u6545\\u4e8b\\u7684\\u5f00\\u59cb\\u3002", "emotion": "happy", "background": "starry_sky", "scene": "good_ending", "ending_type": "good", "is_ending": true}	2026-07-17 03:53:52.057581+00
44444444-4444-4444-4444-444444444448	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444443	ending	{"character": "\\u6797\\u8fb0", "character_id": "22222222-2222-2222-2222-222222222222", "text": "\\u6ca1\\u5173\\u7cfb\\uff0c\\u6211\\u7406\\u89e3\\u3002\\u4e5f\\u8bb8\\u4e0b\\u6b21\\u6709\\u673a\\u4f1a\\u518d\\u89c1\\u3002\\u795d\\u4f60\\u4eca\\u665a\\u6109\\u5feb...\\u661f\\u7a7a\\u4f1a\\u8bb0\\u4f4f\\u6211\\u4eec\\u77ed\\u6682\\u7684\\u76f8\\u9047\\u3002", "emotion": "bittersweet", "background": "cafe_night", "scene": "normal_ending", "ending_type": "normal", "is_ending": true}	2026-07-17 03:53:52.057582+00
44444444-4444-4444-4444-444444444449	33333333-3333-3333-3333-333333333333	44444444-4444-4444-4444-444444444444	ending	{"character": "\\u6797\\u8fb0", "character_id": "22222222-2222-2222-2222-222222222222", "text": "\\u6211\\u660e\\u767d\\u4e86...\\u62b1\\u6b49\\u6253\\u6270\\u4e86\\u3002\\u5e0c\\u671b\\u4f60\\u4eca\\u665a\\u80fd\\u627e\\u5230\\u4f60\\u60f3\\u8981\\u7684...\\u518d\\u89c1\\u3002", "emotion": "sad", "background": "cafe_night", "scene": "bad_ending", "ending_type": "bad", "is_ending": true}	2026-07-17 03:53:52.057583+00
99999999-9999-9999-9999-999999999996	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999993	ending	{"character": "\\u6c88\\u661f\\u6f9c", "character_id": "77777777-7777-7777-7777-777777777777", "text": "\\u6211\\u660e\\u767d\\u4e86...\\u4e5f\\u8bb8\\u6211\\u786e\\u5b9e\\u592a\\u6c89\\u6d78\\u5728\\u81ea\\u5df1\\u7684\\u4e16\\u754c\\u91cc\\u4e86\\u3002\\u62b1\\u6b49\\u6253\\u6270\\u4e86\\u4f60\\u7684\\u591c\\u665a\\u3002\\u6708\\u4eae\\u4f1a\\u7ee7\\u7eed\\u5347\\u8d77\\uff0c\\u800c\\u6211\\u4f1a\\u7ee7\\u7eed\\u89c2\\u6d4b\\u3002\\u518d\\u89c1\\u3002", "emotion": "sad", "background": "observatory_night", "scene": "bad_ending", "ending_type": "bad", "is_ending": true}	2026-07-17 04:03:50.125763+00
a4444444-4444-4444-4444-444444444441	a3333333-3333-3333-3333-333333333333	\N	preset	{"character": "\\u85e4\\u539f\\u96ea", "character_id": "a2222222-2222-2222-2222-222222222222", "text": "\\u4f60\\u597d\\uff0c\\u6211\\u662f\\u85e4\\u539f\\u96ea\\uff0c\\u6587\\u5b66\\u7cfb\\u7684\\u6559\\u6388\\u3002\\u4f60\\u4e5f\\u662f\\u6765\\u770b\\u6a31\\u82b1\\u7684\\u5417\\uff1f\\u6bcf\\u5e74\\u7684\\u8fd9\\u4e2a\\u65f6\\u8282\\uff0c\\u6211\\u90fd\\u4f1a\\u6765\\u8fd9\\u91cc\\u5750\\u4e00\\u4f1a\\u513f\\u3002\\u53e4\\u4eba\\u8bf4\\u300c\\u82b1\\u5f00\\u582a\\u6298\\u76f4\\u987b\\u6298\\u300d\\uff0c\\u6a31\\u82b1\\u7684\\u7f8e\\u603b\\u662f\\u8f6c\\u77ac\\u5373\\u901d...\\u4f60\\u8bfb\\u8fc7\\u591a\\u5c11\\u5173\\u4e8e\\u6a31\\u82b1\\u7684\\u548c\\u6b4c\\u5417\\uff1f", "emotion": "gentle", "background": "cherry_blossom_path", "scene": "opening"}	2026-07-17 04:03:48.538844+00
a4444444-4444-4444-4444-444444444442	a3333333-3333-3333-3333-333333333333	a4444444-4444-4444-4444-444444444441	preset	{"character": "\\u85e4\\u539f\\u96ea", "character_id": "a2222222-2222-2222-2222-222222222222", "text": "\\u771f\\u597d\\uff01\\u4f60\\u5bf9\\u6587\\u5b66\\u7684\\u5174\\u8da3\\u8ba9\\u6211\\u5f88\\u9ad8\\u5174\\u3002\\u5176\\u5b9e\\uff0c\\u6a31\\u82b1\\u5728\\u65e5\\u672c\\u6587\\u5316\\u4e2d\\u8c61\\u5f81\\u7740\\u751f\\u547d\\u7684\\u77ed\\u6682\\u4e0e\\u7f8e\\u4e3d\\u3002\\u5c31\\u50cf\\u8fd9\\u9996\\u548c\\u6b4c\\uff1a\\u300c\\u6a31\\u82b1\\u98d8\\u96f6\\u65f6\\uff0c\\u4f55\\u987b\\u53f9\\u606f\\u58f0\\uff0c\\u4e0d\\u5982\\u5171\\u8d4f\\u6708\\uff0c\\u540c\\u9189\\u6b64\\u591c\\u60c5\\u300d\\u3002\\u4f60\\u613f\\u610f\\u542c\\u6211\\u591a\\u8bb2\\u4e00\\u4e9b\\u5417\\uff1f", "emotion": "delighted", "background": "cherry_blossom_path", "scene": "friendly_path"}	2026-07-17 04:03:48.538846+00
a4444444-4444-4444-4444-444444444443	a3333333-3333-3333-3333-333333333333	a4444444-4444-4444-4444-444444444441	preset	{"character": "\\u85e4\\u539f\\u96ea", "character_id": "a2222222-2222-2222-2222-222222222222", "text": "\\u554a...\\u62b1\\u6b49\\uff0c\\u6211\\u592a\\u5570\\u55e6\\u4e86\\u3002\\u5176\\u5b9e\\u6211\\u53ea\\u662f\\u89c9\\u5f97\\uff0c\\u5728\\u6a31\\u82b1\\u6811\\u4e0b\\u5206\\u4eab\\u6545\\u4e8b\\u662f\\u4e00\\u4ef6\\u5f88\\u7f8e\\u597d\\u7684\\u4e8b\\u3002\\u4f60\\u5982\\u679c\\u53ea\\u662f\\u8def\\u8fc7\\uff0c\\u53ef\\u4ee5\\u7ee7\\u7eed\\u4f60\\u7684\\u6563\\u6b65\\u3002\\u6211\\u53ea\\u662f...\\u6709\\u65f6\\u5019\\u4f1a\\u8fc7\\u4e8e\\u6c89\\u6d78\\u5728\\u81ea\\u5df1\\u7684\\u4e16\\u754c\\u91cc\\u3002", "emotion": "apologetic", "background": "cherry_blossom_path", "scene": "cold_path"}	2026-07-17 04:03:48.538848+00
a4444444-4444-4444-4444-444444444444	a3333333-3333-3333-3333-333333333333	a4444444-4444-4444-4444-444444444442	ending	{"character": "\\u85e4\\u539f\\u96ea", "character_id": "a2222222-2222-2222-2222-222222222222", "text": "\\u592a\\u597d\\u4e86\\uff01\\u5176\\u5b9e...\\u6211\\u6700\\u8fd1\\u6b63\\u5728\\u5199\\u4e00\\u672c\\u5173\\u4e8e\\u6a31\\u82b1\\u4e0e\\u7231\\u60c5\\u7684\\u4e66\\u3002\\u4e5f\\u8bb8\\u6211\\u4eec\\u53ef\\u4ee5\\u4e00\\u8d77\\u6536\\u96c6\\u66f4\\u591a\\u7684\\u7d20\\u6750\\uff1f\\u4e0b\\u5468\\u672b\\u6709\\u4e2a\\u6587\\u5b66\\u6c99\\u9f99\\uff0c\\u5982\\u679c\\u4f60\\u613f\\u610f\\u7684\\u8bdd...\\u6211\\u5f88\\u60f3\\u518d\\u89c1\\u5230\\u4f60\\u3002", "emotion": "happy", "background": "sunset_cherry_blossom", "scene": "good_ending", "ending_type": "good", "is_ending": true}	2026-07-17 04:03:48.538849+00
a4444444-4444-4444-4444-444444444445	a3333333-3333-3333-3333-333333333333	a4444444-4444-4444-4444-444444444442	ending	{"character": "\\u85e4\\u539f\\u96ea", "character_id": "a2222222-2222-2222-2222-222222222222", "text": "\\u6ca1\\u5173\\u7cfb\\uff0c\\u6211\\u7406\\u89e3\\u3002\\u73b0\\u4ee3\\u751f\\u6d3b\\u8282\\u594f\\u5f88\\u5feb\\uff0c\\u4e0d\\u662f\\u6bcf\\u4e2a\\u4eba\\u90fd\\u6709\\u65f6\\u95f4\\u6c89\\u6d78\\u5728\\u6587\\u5b66\\u91cc\\u3002\\u4e0d\\u8fc7...\\u5982\\u679c\\u4f60\\u54ea\\u5929\\u60f3\\u8bfb\\u4e00\\u9996\\u8bd7\\uff0c\\u6216\\u8005\\u53ea\\u662f\\u60f3\\u627e\\u4eba\\u804a\\u804a\\u5929\\uff0c\\u6211\\u7684\\u529e\\u516c\\u5ba4\\u968f\\u65f6\\u6b22\\u8fce\\u4f60\\u3002\\u6a31\\u82b1\\u4f1a\\u8bb0\\u4f4f\\u6211\\u4eec\\u7684\\u76f8\\u9047\\u3002", "emotion": "bittersweet", "background": "cherry_blossom_path", "scene": "normal_ending", "ending_type": "normal", "is_ending": true}	2026-07-17 04:03:48.538849+00
a4444444-4444-4444-4444-444444444446	a3333333-3333-3333-3333-333333333333	a4444444-4444-4444-4444-444444444443	ending	{"character": "\\u85e4\\u539f\\u96ea", "character_id": "a2222222-2222-2222-2222-222222222222", "text": "\\u6211\\u660e\\u767d\\u4e86...\\u4e5f\\u8bb8\\u6211\\u786e\\u5b9e\\u4e0d\\u8be5\\u6253\\u6270\\u4f60\\u7684\\u6563\\u6b65\\u3002\\u62b1\\u6b49\\uff0c\\u6211\\u592a\\u81ea\\u4ee5\\u4e3a\\u662f\\u4e86\\u3002\\u6a31\\u82b1\\u4f1a\\u7ee7\\u7eed\\u98d8\\u843d\\uff0c\\u800c\\u6211\\u4f1a\\u7ee7\\u7eed\\u5728\\u8fd9\\u91cc\\u7b49\\u5f85\\u6709\\u7f18\\u4eba\\u3002\\u795d\\u4f60\\u6709\\u4e2a\\u7f8e\\u597d\\u7684\\u591c\\u665a\\u3002", "emotion": "sad", "background": "cherry_blossom_path", "scene": "bad_ending", "ending_type": "bad", "is_ending": true}	2026-07-17 04:03:48.53885+00
99999999-9999-9999-9999-999999999991	88888888-8888-8888-8888-888888888888	\N	preset	{"character": "\\u6c88\\u661f\\u6f9c", "character_id": "77777777-7777-7777-7777-777777777777", "text": "\\u4f60\\u4e5f\\u662f\\u6765\\u770b\\u6708\\u76f8\\u7684\\u5417\\uff1f\\u4eca\\u665a\\u7684\\u6708\\u4eae\\u6b63\\u597d\\u662f\\u4e0a\\u5f26\\u6708\\uff0c\\u9002\\u5408\\u89c2\\u6d4b\\u6f6e\\u6c50\\u53d8\\u5316\\u3002\\u6211\\u662f\\u6c88\\u661f\\u6f9c\\uff0c\\u5929\\u6587\\u53f0\\u7684\\u7814\\u7a76\\u5458\\u3002\\u4f60\\u770b\\u8d77\\u6765...\\u4e0d\\u50cf\\u662f\\u5929\\u6587\\u5b66\\u7231\\u597d\\u8005\\u3002", "emotion": "curious", "background": "observatory_night", "scene": "opening"}	2026-07-17 04:03:50.125757+00
99999999-9999-9999-9999-999999999992	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999991	preset	{"character": "\\u6c88\\u661f\\u6f9c", "character_id": "77777777-7777-7777-7777-777777777777", "text": "\\u6709\\u610f\\u601d...\\u4f60\\u5bf9\\u661f\\u8fb0\\u7684\\u597d\\u5947\\u5fc3\\u8ba9\\u6211\\u60f3\\u8d77\\u4e86\\u81ea\\u5df1\\u521a\\u5f00\\u59cb\\u7814\\u7a76\\u5929\\u6587\\u5b66\\u7684\\u65f6\\u5019\\u3002\\u5176\\u5b9e\\uff0c\\u6708\\u76f8\\u4e0d\\u4ec5\\u5f71\\u54cd\\u6f6e\\u6c50\\uff0c\\u5728\\u53e4\\u8001\\u7684\\u5360\\u661f\\u5b66\\u4e2d\\uff0c\\u6708\\u4eae\\u7684\\u4f4d\\u7f6e\\u88ab\\u8ba4\\u4e3a\\u4f1a\\u5f71\\u54cd\\u4eba\\u7684\\u547d\\u8fd0\\u3002\\u4f60\\u76f8\\u4fe1\\u5417\\uff1f", "emotion": "intrigued", "background": "observatory_night", "scene": "friendly_path"}	2026-07-17 04:03:50.125759+00
99999999-9999-9999-9999-999999999993	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999991	preset	{"character": "\\u6c88\\u661f\\u6f9c", "character_id": "77777777-7777-7777-7777-777777777777", "text": "\\u554a...\\u62b1\\u6b49\\uff0c\\u6211\\u4e60\\u60ef\\u4e86\\u7528\\u4e13\\u4e1a\\u672f\\u8bed\\u3002\\u5176\\u5b9e\\u6211\\u53ea\\u662f\\u60f3\\u8bf4\\uff0c\\u4eca\\u665a\\u7684\\u6708\\u4eae\\u5f88\\u7f8e\\uff0c\\u9002\\u5408\\u4e00\\u4e2a\\u4eba\\u9759\\u9759\\u5730\\u770b\\u3002\\u4f60\\u5982\\u679c\\u6ca1\\u4ec0\\u4e48\\u4e8b\\u7684\\u8bdd\\uff0c\\u53ef\\u4ee5\\u7ee7\\u7eed\\u4f60\\u7684\\u6563\\u6b65\\u3002", "emotion": "disappointed", "background": "observatory_night", "scene": "cold_path"}	2026-07-17 04:03:50.12576+00
99999999-9999-9999-9999-999999999994	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	ending	{"character": "\\u6c88\\u661f\\u6f9c", "character_id": "77777777-7777-7777-7777-777777777777", "text": "\\u592a\\u597d\\u4e86\\uff01\\u5176\\u5b9e...\\u6211\\u4e00\\u76f4\\u60f3\\u627e\\u4eba\\u5206\\u4eab\\u8fd9\\u4e9b\\u3002\\u4e5f\\u8bb8\\u6211\\u4eec\\u53ef\\u4ee5\\u4e00\\u8d77\\u89c2\\u6d4b\\u4e0b\\u4e00\\u6b21\\u7684\\u6708\\u5168\\u98df\\uff1f\\u636e\\u8bf4\\u90a3\\u4f1a\\u662f\\u975e\\u5e38\\u7f55\\u89c1\\u7684\\u5929\\u8c61\\u3002\\u8fd9\\u7b97\\u662f...\\u6211\\u4eec\\u7684\\u7ea6\\u5b9a\\u5417\\uff1f", "emotion": "happy", "background": "moonlit_sky", "scene": "good_ending", "ending_type": "good", "is_ending": true}	2026-07-17 04:03:50.125761+00
99999999-9999-9999-9999-999999999995	88888888-8888-8888-8888-888888888888	99999999-9999-9999-9999-999999999992	ending	{"character": "\\u6c88\\u661f\\u6f9c", "character_id": "77777777-7777-7777-7777-777777777777", "text": "\\u6ca1\\u5173\\u7cfb\\uff0c\\u6211\\u7406\\u89e3\\u3002\\u79d1\\u5b66\\u7814\\u7a76\\u9700\\u8981\\u5927\\u91cf\\u7684\\u65f6\\u95f4\\u6295\\u5165\\u3002\\u4e0d\\u8fc7...\\u5982\\u679c\\u4f60\\u54ea\\u5929\\u5bf9\\u5929\\u6587\\u5b66\\u611f\\u5174\\u8da3\\u4e86\\uff0c\\u5929\\u6587\\u53f0\\u968f\\u65f6\\u6b22\\u8fce\\u4f60\\u3002\\u4eca\\u665a\\u7684\\u6708\\u8272\\uff0c\\u6211\\u4f1a\\u8bb0\\u4f4f\\u7684\\u3002", "emotion": "bittersweet", "background": "observatory_night", "scene": "normal_ending", "ending_type": "normal", "is_ending": true}	2026-07-17 04:03:50.125762+00
\.


--
-- Data for Name: oauth_accounts; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.oauth_accounts (id, user_id, provider, provider_user_id, created_at) FROM stdin;
05598d3e-0c05-422c-a288-07ab0fbf2a0d	df8754f6-e00d-4406-8d2c-e2ac8895a3d0	wechat	mock_wechat_test123	2026-07-17 06:14:42.71883+00
2d2c818a-a325-491c-83db-fa12f398b800	0854f0a4-eee9-421f-805c-f6ff54fd3b94	google	mock_google_test456	2026-07-17 06:14:42.727123+00
ca98d698-9637-45f4-97cd-5ad6753bdbb4	9e870e7e-6382-4b75-bf73-d01d7511bb1c	apple	mock_apple_test789	2026-07-17 06:14:42.7329+00
586808a7-5a91-4438-b6f5-03f225a20d1a	56dca9da-10ab-43f7-83f4-89acd58f5bb7	google	mock_google_***	2026-07-17 06:35:32.774002+00
07a06447-af3a-42b7-80a2-3bb7b5f8b0c6	b30e40e5-943b-4a55-b05b-59e744365acf	wechat	mock_wechat_mock-code-123	2026-07-17 08:50:04.89496+00
e646c59c-4373-4f5b-b49b-3ffb924fdde8	cac23f0a-8424-4ec9-b51e-076ccd031502	google	mock_google_mock-code-123	2026-07-17 08:50:04.900848+00
e37f8c83-5d6f-44f4-88ae-88bfee498507	eaf488f4-6042-4e4a-878d-dcc4a2f4d148	apple	mock_apple_mock-code-123	2026-07-17 08:50:04.906602+00
4aab888f-4b94-48a1-a509-f2f57bc8a3b0	b10ecf0e-d237-4db4-8dc2-d3a75ad357d9	google	mock_google_mock_code_123	2026-07-17 09:07:44.85432+00
47475bab-033b-414a-97d9-d3ac63532ab9	6e76cf29-a71d-4254-8653-3b229a20b841	wechat	mock_wechat_unique_code_0	2026-07-17 10:02:30.568585+00
c482ce21-b8da-4bf8-843d-d2362d7cc978	6bdf0762-b72b-4c37-8d27-7a7620028e9c	wechat	mock_wechat_unique_code_1	2026-07-17 10:02:30.831826+00
1bd3f54c-e5c0-4779-8a86-3c098d0bd488	504e20ad-4cdf-4ed9-b5fc-bc6cb3088414	wechat	mock_wechat_unique_code_2	2026-07-17 10:02:31.094442+00
c6beadb2-f69d-4343-8b97-88e5155b7bb8	c403e517-66af-4d05-98b2-22e88b9fe19f	wechat	mock_wechat_unique_code_3	2026-07-17 10:02:31.357012+00
6a7ed912-10c0-43d7-83fc-7e3e4330ab1c	6371f8d0-3ac6-4f95-9ab1-3759ef65d357	wechat	mock_wechat_unique_code_4	2026-07-17 10:02:31.61953+00
41093e3e-1ae7-46ba-a5af-e6bbe5cc1bd3	1abe0211-2cc7-4450-8229-6d5af84031c2	wechat	mock_wechat_unique_code_5	2026-07-17 10:02:31.882164+00
d6c09844-26d1-493d-98c8-c0c950d58820	055c07fb-d06a-4338-ad5b-ca9fd503fa59	wechat	mock_wechat_unique_code_6	2026-07-17 10:02:32.146067+00
ba729c11-b496-4f00-ac51-31c685e3f422	33127d9c-d74c-43db-b146-aa4079457d0d	wechat	mock_wechat_unique_code_7	2026-07-17 10:02:32.409233+00
72d303c8-a2da-431d-953f-f617ffe6e38b	8cfa12ce-cbd4-4982-b5ed-34b69f0a1b04	wechat	mock_wechat_unique_code_8	2026-07-17 10:02:32.67125+00
0375883b-63da-46f5-be91-ec84f2621e33	092e8d09-04e6-4d32-8088-062a3d0d20d9	wechat	mock_wechat_unique_code_9	2026-07-17 10:02:32.933164+00
\.


--
-- Data for Name: password_resets; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.password_resets (id, user_id, token, expires_at, used, created_at) FROM stdin;
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.posts (id, user_id, title, content, image_urls, like_count, comment_count, is_deleted, created_at, updated_at) FROM stdin;
f43d176a-6726-4045-8e64-e8e2698f5e47	fbc9e9fd-e41f-4c25-9ebe-bd48d894807f	测试帖子	这是一个测试帖子内容	\N	0	1	f	2026-07-17 06:16:11.652165+00	2026-07-17 06:16:11.672382+00
030bb84d-d494-41c3-9415-15e90314c51f	2ae26db0-76cd-4d01-8033-8727a4c31dde	Test Post	Hello world	\N	0	0	f	2026-07-17 06:34:11.039847+00	2026-07-17 06:34:11.039849+00
19f1a3a9-520f-46af-8724-5e0512c4f9e5	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	Test from FE	Hello from frontend	\N	0	0	f	2026-07-17 06:35:41.647059+00	2026-07-17 06:35:41.647061+00
5f4fbd4f-9265-464f-b31a-0e90a3baf15b	4c4df553-0ff6-4cbd-b294-12e24cefa68a	Test	Hello	\N	0	0	f	2026-07-17 06:48:03.264149+00	2026-07-17 06:48:03.264152+00
4777d9b9-5e9b-4142-8ea7-c1a1ac7bc6af	8ddc774b-6361-468d-9f3f-b32553bd0efe	Integration Test	Testing UGC	\N	0	1	f	2026-07-17 07:09:38.023239+00	2026-07-17 07:09:38.038182+00
974c9bba-5a8f-46a0-9564-47653bf1a7e0	cfcfa1c1-66b5-4334-97b5-c626091beb34	Test Post	UGC content	\N	0	1	f	2026-07-17 07:13:17.926074+00	2026-07-17 07:13:17.942864+00
d1e1a4ee-b6aa-4dd7-a4e6-92c5147bead4	4cde0b80-2b46-4081-b6af-8e70be92e8e7	联调测试帖	这是联调验证内容	\N	0	0	f	2026-07-17 08:49:15.867258+00	2026-07-17 08:49:15.86726+00
bf89e285-08bc-4b3c-a273-5cc8843b9adb	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	联调测试帖	这是联调验证内容	\N	0	0	f	2026-07-17 08:50:05.004469+00	2026-07-17 08:50:05.004472+00
7c0d4788-3c4d-4ef4-b0d1-643e58fd5260	778dfb6a-46f5-415d-a114-35173f8d8893	联调测试帖	这是联调验证内容	\N	0	0	f	2026-07-17 09:03:54.39136+00	2026-07-17 09:03:54.391362+00
\.


--
-- Data for Name: purchases; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.purchases (id, user_id, item_id, item_name, price, currency, is_mock, created_at) FROM stdin;
9cfd08c2-76c7-4ea1-bf8c-d8cfe84d03d9	f016da07-7326-4763-a309-c471722195ab	fragments_100	100 Fragments	0.99	USD	t	2026-07-17 06:13:22.511594+00
1b730961-9097-4a95-9380-4e9b7956cb55	ecfc3e91-fb50-4985-b8c4-55c479d6e8b6	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 06:32:20.373076+00
ffc5b952-8103-42f4-97c6-a2971d79aa49	27620270-1362-460a-b84a-defc09135cb8	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 06:33:05.226271+00
8242ffcf-121e-46e7-99df-85e60493af1c	2ae26db0-76cd-4d01-8033-8727a4c31dde	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 06:34:11.001414+00
42ee9284-0f73-4d72-8fd8-47007aa5f2f8	2ae26db0-76cd-4d01-8033-8727a4c31dde	script-001	星辰之约	9.99	USD	t	2026-07-17 06:35:32.753128+00
486cccff-aeb7-4ed6-9682-6c93bc605db3	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	shards_100	100碎片	6.00	USD	t	2026-07-17 06:35:53.218322+00
c94443a9-0505-4595-bd2f-dc183b18b9e2	4c4df553-0ff6-4cbd-b294-12e24cefa68a	script-001	test	9.99	USD	t	2026-07-17 06:48:03.199083+00
7f334b28-22fd-4e8e-a2c4-c1fec2c5a295	4c4df553-0ff6-4cbd-b294-12e24cefa68a	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 06:48:03.216387+00
df15957b-8bc1-4d2e-b95c-8b94ef4e5906	8ddc774b-6361-468d-9f3f-b32553bd0efe	shards-100	碎片100	4.99	USD	t	2026-07-17 07:09:37.992641+00
af1689b1-dabd-4f97-99dc-fffe1985f1f4	8ddc774b-6361-468d-9f3f-b32553bd0efe	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 07:09:38.008286+00
0030193f-f422-4bbd-a04b-20afb829806c	cfcfa1c1-66b5-4334-97b5-c626091beb34	shards-100	碎片100	4.99	USD	t	2026-07-17 07:13:17.8963+00
906f1f10-fe89-479a-aadb-adcf50fb25c6	cfcfa1c1-66b5-4334-97b5-c626091beb34	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 07:13:17.909679+00
98802a7f-abd7-4b54-954f-a3092a23b200	4cde0b80-2b46-4081-b6af-8e70be92e8e7	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 08:49:15.846376+00
e359db0f-9e1a-470e-97a8-adb0a9f2e1b5	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 08:50:04.978874+00
98c9a1cc-7925-4e76-8034-0369114f650e	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 08:50:04.984712+00
1189c982-6bcf-4d55-9a3e-97dff729d8cb	778dfb6a-46f5-415d-a114-35173f8d8893	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 09:03:54.360985+00
dff6ee09-f0da-4368-bd77-ddff6e89821c	778dfb6a-46f5-415d-a114-35173f8d8893	fragments_100	100 Fragments	4.99	USD	t	2026-07-17 09:03:54.366928+00
c909528c-51dc-425b-8d25-24fe05a1be82	3e9b3ff7-ccbf-47ba-99ef-1a890bd513c7	fragments_100	100 Fragments	0.99	USD	t	2026-07-17 09:07:44.863733+00
\.


--
-- Data for Name: routes; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.routes (id, script_id, title, description, created_at) FROM stdin;
33333333-3333-3333-3333-333333333333	11111111-1111-1111-1111-111111111111	星夜邂逅	在咖啡厅的偶然相遇，开启了一段星辰交织的故事	2026-07-17 03:53:52.055754+00
a3333333-3333-3333-3333-333333333333	a1111111-1111-1111-1111-111111111111	樱花树下	在樱花盛开的校园小径上，一段诗意的邂逅	2026-07-17 04:03:48.536953+00
88888888-8888-8888-8888-888888888888	66666666-6666-6666-6666-666666666666	月夜邂逅	在天文台的偶然相遇，开启了一段星月交织的奇幻故事	2026-07-17 04:03:50.123856+00
\.


--
-- Data for Name: scenes; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.scenes (id, script_id, name, background_url, bgm_url, created_at) FROM stdin;
\.


--
-- Data for Name: scripts; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.scripts (id, slug, title, description, genre, cover_image_url, created_at, updated_at) FROM stdin;
11111111-1111-1111-1111-111111111111	starry-vow	星辰之约	在星光璀璨的夜晚，你与温柔的占星师林辰相遇。命运的齿轮开始转动，你们的故事即将展开...	romance	/assets/covers/starry-vow.jpg	2026-07-17 03:53:52.052008+00	2026-07-17 03:53:52.052012+00
a1111111-1111-1111-1111-111111111111	cherry-blossom-romance	樱花恋曲	在樱花盛开的季节，你与温柔的文学教授藤原雪相遇。古典文学与现代情感的碰撞，开启了一段诗意的恋情...	romance	/assets/covers/cherry-blossom-romance.jpg	2026-07-17 04:03:48.533677+00	2026-07-17 04:03:48.53368+00
66666666-6666-6666-6666-666666666666	star-moon-fate	星月奇缘	在神秘的月夜下，你与天才天文学家沈星澜相遇。星辰与月光的交织，开启了一段奇幻的缘分...	romance	/assets/covers/star-moon-fate.jpg	2026-07-17 04:03:50.120723+00	2026-07-17 04:03:50.120726+00
\.


--
-- Data for Name: share_cards; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.share_cards (id, user_id, share_type, title, description, image_url, extra_data, created_at) FROM stdin;
bcc363f0-c471-4c4a-9330-479ee974c50e	28f0f2b9-c8fa-42dd-aa73-9b4e277ec2b7	game_result	我的游戏结局	达成了完美结局！	\N	{"ending": "good", "script_id": "111"}	2026-07-17 06:18:56.975219+00
fb772f40-e364-4117-87f0-26a8d7be2dfa	2ae26db0-76cd-4d01-8033-8727a4c31dde	ending	星辰之约完美结局	好感度满级达成！	\N	{}	2026-07-17 06:35:32.780154+00
aeca9725-451e-4b3c-9dd9-74875d1b9fc3	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	ending	星辰之约	\N	\N	{}	2026-07-17 06:35:53.229132+00
c6ac3840-092d-4c83-8526-33c9dd4f2037	4c4df553-0ff6-4cbd-b294-12e24cefa68a	ending	Test Share	\N	\N	{}	2026-07-17 06:48:03.295279+00
33e74c22-d68a-4d41-bbd6-38e7ecb5c0d2	8ddc774b-6361-468d-9f3f-b32553bd0efe	ending	Test Share	\N	\N	{}	2026-07-17 07:09:38.065403+00
3ff12409-f21a-40de-9a47-162850ced757	cfcfa1c1-66b5-4334-97b5-c626091beb34	ending	Test Share	\N	\N	{}	2026-07-17 07:13:17.986152+00
53e03fd7-56c1-4b1a-92af-14c7164152b4	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	game_result	联调分享卡片	分享测试内容	\N	{}	2026-07-17 08:50:05.010002+00
5948f910-38f8-4b5f-8d5c-162536f5e28e	778dfb6a-46f5-415d-a114-35173f8d8893	game_result	联调分享卡片	分享测试内容	\N	{}	2026-07-17 09:03:54.398375+00
0b72c037-7a61-4baa-9ee3-88c0070d48e5	3e9b3ff7-ccbf-47ba-99ef-1a890bd513c7	ending	Test Ending	\N	\N	{}	2026-07-17 09:07:44.840401+00
\.


--
-- Data for Name: streak_records; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.streak_records (id, user_id, current_streak, max_streak, last_checkin_date, updated_at) FROM stdin;
62cc8bd7-0b26-4d29-a161-5c53a76e61b9	c4444a36-cfdb-4be6-ae51-25df8e615865	1	1	2026-07-17	2026-07-17 03:02:01.269016+00
4c939632-8d88-43fb-adc8-c8ee2e452b29	3da05a2a-43ba-424a-8f97-fb2256804474	1	1	2026-07-17	2026-07-17 03:46:09.283263+00
d1483384-c817-4bdb-8d15-d2b93ad52907	c17290b0-dcea-42db-836a-937446784655	1	1	2026-07-17	2026-07-17 04:37:55.260451+00
7324485d-94fa-4769-8723-a41a857a77d2	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	1	1	2026-07-17	2026-07-17 05:02:38.349142+00
4e91fc35-dab3-4db4-8c18-68e89664e001	71534de5-9bbb-4e62-8130-7b0488eb3faa	1	1	2026-07-17	2026-07-17 05:17:02.313172+00
3b6eb59d-fde5-4992-ab4e-d917b5258f7a	2ae26db0-76cd-4d01-8033-8727a4c31dde	1	1	2026-07-17	2026-07-17 06:34:10.900151+00
ecd525f3-4f59-4f0c-b62e-7449b585ce41	4c4df553-0ff6-4cbd-b294-12e24cefa68a	1	1	2026-07-17	2026-07-17 06:48:03.005277+00
4a5ae9ab-33cf-4964-9e33-047c631719b8	8ddc774b-6361-468d-9f3f-b32553bd0efe	1	1	2026-07-17	2026-07-17 07:09:37.888101+00
5bccd1dd-3f38-4b19-b40a-d49a3689dde9	cfcfa1c1-66b5-4334-97b5-c626091beb34	1	1	2026-07-17	2026-07-17 07:13:17.80419+00
b673e8c1-8016-43b5-ab08-b4461be6885c	4cde0b80-2b46-4081-b6af-8e70be92e8e7	1	1	2026-07-18	2026-07-17 08:49:15.82165+00
29a9bce4-bf1e-4994-af80-98c91113b9bb	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	1	1	2026-07-18	2026-07-17 08:50:04.95611+00
7a86b911-c93b-4323-a611-2b1f39b10d24	778dfb6a-46f5-415d-a114-35173f8d8893	1	1	2026-07-18	2026-07-17 09:03:54.339458+00
e67f2fdc-b04c-4110-994a-ffa710b95e8a	3e9b3ff7-ccbf-47ba-99ef-1a890bd513c7	1	1	2026-07-18	2026-07-17 09:06:08.678109+00
72115955-9cf1-4261-978f-01f7b3464750	5bcd3ab0-458d-4e0c-856a-5436b8c78662	1	1	2026-07-18	2026-07-17 09:08:56.517391+00
5163fb69-51d4-4334-b803-21117562c64c	1697729c-6110-45f9-b44c-0811949f0fb7	1	1	2026-07-18	2026-07-17 09:08:57.15301+00
d233f175-a4fd-42f7-8610-f78f0d1e9540	a2ba87f5-51a8-40c7-b84e-d46a48332cf4	1	1	2026-07-18	2026-07-17 09:10:21.730261+00
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.subscriptions (id, user_id, plan_id, status, billing_cycle, currency, price, is_mock, started_at, expires_at, cancelled_at) FROM stdin;
2bb8e200-7d9c-45f0-970d-a83dcc00eda3	f016da07-7326-4763-a309-c471722195ab	basic	cancelled	monthly	USD	4.99	t	2026-07-17 06:13:22.494553+00	2026-08-16 06:13:22.493691+00	2026-07-17 06:13:22.503741+00
7d14237f-d2b4-4887-8158-9230d6d1c017	f016da07-7326-4763-a309-c471722195ab	premium	active	yearly	USD	99.99	t	2026-07-17 06:13:22.504946+00	2027-07-17 06:13:22.503749+00	\N
9ba1614f-5d2d-4133-8512-4a187995a8fd	ecfc3e91-fb50-4985-b8c4-55c479d6e8b6	premium	active	monthly	USD	9.99	t	2026-07-17 06:32:20.357546+00	2026-08-16 06:32:20.356718+00	\N
4f4f14d7-bcf1-4521-9a8d-76e70391870c	27620270-1362-460a-b84a-defc09135cb8	premium	active	monthly	USD	9.99	t	2026-07-17 06:33:05.215814+00	2026-08-16 06:33:05.215494+00	\N
1422972a-c8aa-44bb-8f07-c6f0db10a3fb	2ae26db0-76cd-4d01-8033-8727a4c31dde	basic	active	monthly	USD	4.99	t	2026-07-17 06:35:32.763132+00	2026-08-16 06:35:32.762763+00	\N
94b228d7-37fe-4f89-9577-bfd06f0fad48	b305c5e0-cdac-47e7-a718-c5a4b84f7df0	basic	active	monthly	USD	4.99	t	2026-07-17 06:35:53.206649+00	2026-08-16 06:35:53.206256+00	\N
e80247ea-9279-41e2-8bad-f39ef11996f8	4c4df553-0ff6-4cbd-b294-12e24cefa68a	basic	active	monthly	USD	4.99	t	2026-07-17 06:48:03.234573+00	2026-08-16 06:48:03.23376+00	\N
42df61fe-b8d3-43ff-8936-47870282e8c6	8ddc774b-6361-468d-9f3f-b32553bd0efe	basic	active	monthly	USD	4.99	t	2026-07-17 07:09:37.969311+00	2026-08-16 07:09:37.910167+00	\N
149959e5-e0b9-42b0-873c-a83c8a555a75	cfcfa1c1-66b5-4334-97b5-c626091beb34	basic	active	monthly	USD	4.99	t	2026-07-17 07:13:17.881508+00	2026-08-16 07:13:17.880606+00	\N
e465e7a1-c003-4c55-9b92-619ba86f89b0	4cde0b80-2b46-4081-b6af-8e70be92e8e7	premium	active	monthly	USD	9.99	t	2026-07-17 08:49:15.833703+00	2026-08-16 08:49:15.833063+00	\N
439209d4-ae20-4cc6-84ed-8398404466d4	04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	premium	active	monthly	USD	9.99	t	2026-07-17 08:50:04.967375+00	2026-08-16 08:50:04.967098+00	\N
cf1c70d1-f01a-4b0a-8305-c7bb1758376c	778dfb6a-46f5-415d-a114-35173f8d8893	premium	active	monthly	USD	9.99	t	2026-07-17 09:03:54.349998+00	2026-08-16 09:03:54.349722+00	\N
91e9363a-0e78-4fe8-bede-d884bca3f2bb	47680d40-c99b-4ba0-a44a-ecd335f46dfb	basic	active	monthly	USD	4.99	t	2026-07-17 09:19:40.782916+00	2026-08-16 09:19:40.781643+00	\N
\.


--
-- Data for Name: unlocked_cgs; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.unlocked_cgs (id, user_id, cg_id, unlocked_at) FROM stdin;
\.


--
-- Data for Name: unlocked_scripts; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.unlocked_scripts (id, user_id, script_id, unlocked_at) FROM stdin;
\.


--
-- Data for Name: user_preferences; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.user_preferences (id, user_id, language, bgm_enabled, sfx_enabled, text_speed, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: isekai
--

COPY public.users (id, email, password_hash, display_name, avatar_url, email_verified, oauth_provider, oauth_id, subscription_tier, trial_started_at, trial_ends_at, onboarding_completed, preferred_genre, locale, created_at, updated_at) FROM stdin;
bd7f90f9-f543-4fb0-98eb-b9c2a42410a2	demo@isekai.dev	$2b$12$PLU65IfkpsPWT6no2fANAOtqTpP5cxIqHrZjV6sF3F6.ElnLE2I5m	demo	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 02:40:05.754731+00	2026-07-17 02:40:05.754735+00
05258f2e-e923-4fa4-b9bb-9de776ea31bb	test@example.com	$2b$12$ZinyoK4HWIar.LbUjngS7eNCOw0g5po1/QfVeuBTDF1mPdSpfpcri	test	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 02:48:57.775043+00	2026-07-17 02:48:57.775048+00
c4444a36-cfdb-4be6-ae51-25df8e615865	verify@example.com	$2b$12$5ArAxaueSuOXynVqH9ERgOv50irV4mGKpLe9C.ils3frVI2H/h.L.	verify	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 03:02:01.243875+00	2026-07-17 03:02:01.243879+00
3da05a2a-43ba-424a-8f97-fb2256804474	final@example.com	$2b$12$WMBtafYZtRF3.kziBG.UkOv/Xx3jr2YfmzaowVlbj00l3opb5ICam	final	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 03:46:09.257992+00	2026-07-17 03:46:09.257997+00
8ae9f59c-42b2-415f-a415-7743120c2637	seed@example.com	$2b$12$6KmnV9u5e7BSK1hFv0V4MO2Nl9TJMoeoEbn/CoiCMnsmTmh2mkBf6	Seed User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 03:51:36.069875+00	2026-07-17 03:51:36.06988+00
198a83dc-6bba-4c2c-af10-90a8711f26d0	player@example.com	$2b$12$bqTZ2j/zFFujhgoRd0CTfed5ckOZ8r/nZ.cvBS2wHWcpjuXnW1q0K	Test Player	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 03:55:13.106249+00	2026-07-17 03:55:13.106253+00
d474b2b6-0bdb-4b67-b76a-bee0783328a8	verify@dev.com	$2b$12$S24f9VDH1V6S0r0x/YyhVeqLM/l.k9WeSytwx1SKXrFBiaCIuDvBm	Verify	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 04:04:02.049977+00	2026-07-17 04:04:02.049981+00
8c9beb2b-5c24-4de2-bf56-433271037507	test_1784290175@example.com	$2b$12$sdbQfn39nD9wfAU4GjJv9ui28JEqRlWUxTu1pMO6hBED7uLKBHV76	Test User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 04:09:35.615936+00	2026-07-17 04:09:35.61594+00
6f583b94-a4f6-47e4-a611-bd9ca902eb0a	test-dev012@example.com	$2b$12$DZSjIscUh92W6/4ABj/IDe44I4Poc2BbwLuSzyMdOl0a/Imk4Gig6	DEV012 Tester	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 04:37:18.718083+00	2026-07-17 04:37:18.718087+00
c17290b0-dcea-42db-836a-937446784655	e2e-***@example.com	$2b$12$tyZcd5crq/aQ0Y9kn0csluW54m/69v0GoU7uXO1R2YvDSaOKvmiIK	e2e-***	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 04:37:42.934344+00	2026-07-17 04:37:42.934349+00
8084ea10-5492-4d6d-a37b-29eacac32b81	e2e-final2@example.com	$2b$12$9QtiX1CAwM5GPUEo/BG/OOSuQMpnX3mTh42OHRBUpe/5pb2t7j1je	e2e-final2	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 05:15:56.437908+00	2026-07-17 05:15:56.437912+00
d28744c5-a162-4f66-aca0-393f2a6ec27a	e2e-verify@example.com	$2b$12$r385W9WNH93NdXFrzBXC3uOV6uRJQb5ffdqKD5HKIoYTmiowT4VBi	e2e-verify	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 05:16:30.887516+00	2026-07-17 05:16:30.88752+00
71534de5-9bbb-4e62-8130-7b0488eb3faa	e2e-v2@example.com	$2b$12$.DtHbLmll4UjJMlaMwlSVOCZUrEyllHK6MmhF7b7JCwqJuYwYI3wG	e2e-v2	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 05:17:01.983769+00	2026-07-17 05:17:01.983772+00
d410f5c2-be93-4ca9-82e4-23d9ffb0a33f	e2e-1784294715404@wanderer.com	$2b$12$oP0QttpXdBHQY1rYhB.mpe/GMyOeHmkOiCiPmVtPpAj6gLuNlRYHa	e2e-1784294715404	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 05:25:16.423295+00	2026-07-17 05:25:16.423299+00
66843c4f-e0ac-4b16-9f31-be5fa1eb444f	e2e-1784294825401@wanderer.com	$2b$12$0y8lWTrc3BGaqtdosWPtduAlFEoHFbk2esNZqArlFlmuVlE.6sLuW	e2e-1784294825401	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 05:27:06.480988+00	2026-07-17 05:27:06.480991+00
5cf0d44b-4b01-4f27-9969-595adff606ad	e2e-1784294943317@wanderer.com	$2b$12$udG3J0IIutkMPy1gB6RMV.WPPYJuFmoiONL9EEeNdkXpnFfdS0Mei	e2e-1784294943317	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 05:29:04.555149+00	2026-07-17 05:29:04.555158+00
f175ddf9-86d2-4670-8a05-e6c31b18aea9	plfix01@test.com	$2b$12$Kr9oXRqvyIy/VxUSKs96det01vRHLQvaF3wZDYeWMTlX9seOuDhLS	PL Fix Tester	\N	t	\N	\N	free	\N	\N	t	\N	en	2026-07-17 05:47:48.212176+00	2026-07-17 05:47:48.574879+00
735b1c47-8e0b-4184-9423-483014ad595c	e2e-1784296101152@wanderer.com	$2b$12$JoMD7TIua5bL0EI53zKdv.mXZnD/Ci0435b3Ye0b65VcYj6Ec77.q	e2e-1784296101152	\N	t	\N	\N	free	\N	\N	t	\N	en	2026-07-17 05:48:22.204686+00	2026-07-17 05:48:27.45141+00
6d31dec5-c0e2-4abc-abdd-27143cf02628	fealign@test.com	$2b$12$zhcuGHZDcCM0w14ej3.bReeu4C8HGIhQrMiAHKmpcSz46be3pFynC	fealign	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 05:50:52.731671+00	2026-07-17 05:50:52.731675+00
3f5f6396-b061-4d34-82c2-fb6f43942033	fealign2@test.com	$2b$12$PboMRYxMd.zlKaPzyc3.auGT3cp8MIYL7radRDjnEuLMCEW5tFqUu	fealign2	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 05:52:00.558248+00	2026-07-17 05:52:00.568858+00
0af81174-e857-4e63-b114-6973568adb25	phase3check@test.com	$2b$12$788x1XHRq3p6rmTlGYTTHuVy/jUmjM2lPTATEqyoEXBEpq5qDaR.m	phase3check	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 06:09:49.887672+00	2026-07-17 06:09:50.155581+00
f016da07-7326-4763-a309-c471722195ab	pay01@test.com	$2b$12$bItT7XXN16ZYBrpF48SgiOIBgD73I8yVOftYlOnreCSziJG5.SAbW	pay01	\N	t	\N	\N	premium	\N	\N	f	\N	en	2026-07-17 06:13:22.478471+00	2026-07-17 06:13:22.506109+00
df8754f6-e00d-4406-8d2c-e2ac8895a3d0	mock_wechat_test123@oauth.mock	\N	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 06:14:42.717105+00	2026-07-17 06:14:42.717109+00
0854f0a4-eee9-421f-805c-f6ff54fd3b94	mock_google_test456@oauth.mock	\N	Google User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 06:14:42.726435+00	2026-07-17 06:14:42.726438+00
9e870e7e-6382-4b75-bf73-d01d7511bb1c	mock_apple_test789@oauth.mock	\N	Apple User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 06:14:42.732275+00	2026-07-17 06:14:42.732278+00
fbc9e9fd-e41f-4c25-9ebe-bd48d894807f	ugc@test.com	$2b$12$d9h0nCxxtH4bX5uFvD3g6uc2awtmdoOTvwsV/ifEkumeIDrlq4ZyW	ugc	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 06:16:11.638288+00	2026-07-17 06:16:11.638293+00
e2646edb-d91c-463e-96d9-739f2dd74b3e	share@test.com	$2b$12$nyCflS6FB62ayEwBYRoe2ur.a8azU6K52QOgzdMINoc2AvblqNb9S	share	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 06:18:08.133645+00	2026-07-17 06:18:08.133649+00
28f0f2b9-c8fa-42dd-aa73-9b4e277ec2b7	share2@test.com	$2b$12$T2mDXp5u/JWshhsbosu6TOSrIpKVCixYx3Ikz51xOrcMEQpSQLT9y	share2	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 06:18:56.962642+00	2026-07-17 06:18:56.962647+00
5c7d7fd6-5b64-420a-bc37-1cb72996b998	gallery2@test.com	$2b$12$y6HoG84pOrqOl.sw8ZnESOvY31jSH.V6erYGWW6GHVXLz95BuCWM.	gallery2	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 06:21:32.268383+00	2026-07-17 06:21:32.268387+00
6ee18a17-7ca4-4f67-9a8e-c0f346212ad4	e2e-1784298462770@wanderer.com	$2b$12$cQ6oBVzj3NEKz1Z3gXCS8OMY0wG8663J39F1o59dpiu2oNYZKp2CW	e2e-1784298462770	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 06:27:43.860275+00	2026-07-17 06:27:49.095353+00
8ddc774b-6361-468d-9f3f-b32553bd0efe	integ1784300977@test.com	$2b$12$T9lEHvbPR.qzyxVfdEypA.gU3PlraKC5WI41DpDcD4mSEa9RsVDEW	integ1784300977	\N	t	\N	\N	basic	\N	\N	t	\N	en	2026-07-17 07:09:37.557579+00	2026-07-17 07:09:37.977969+00
ecfc3e91-fb50-4985-b8c4-55c479d6e8b6	p1fix@test.com	$2b$12$nxNII6fIEMoWYS/9ZwiHk.oAV96WJn70rsvNPcs4DAjb3CiBRKlT2	p1fix	\N	t	\N	\N	premium	\N	\N	t	romance	zh	2026-07-17 06:32:20.337845+00	2026-07-17 06:32:20.388924+00
27620270-1362-460a-b84a-defc09135cb8	p1fix2@test.com	$2b$12$sR5.JLhRmbsxzkcX.gjcO.R8OUmfTk4tyE9m.Sxa5VzZ8nwWygCry	p1fix2	\N	t	\N	\N	premium	\N	\N	t	romance	zh	2026-07-17 06:33:05.202626+00	2026-07-17 06:33:05.239527+00
ec6ecb8e-4be5-4ebb-99ea-a1c4e88baf59	e2e-1784301253376@wanderer.com	$2b$12$pshsaMWIGzaq.0J5dPel0OtB9foqRHva2rLYZdelbjdhTgAMBbQpG	e2e-1784301253376	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 07:14:14.464949+00	2026-07-17 07:14:19.708538+00
2ae26db0-76cd-4d01-8033-8727a4c31dde	final_check@test.com	$2b$12$29v1FslQFy78Oy8K3CixdOIupZE..tlyl/p4F.B96U0GX7vsw02gq	final_check	\N	t	\N	\N	basic	\N	\N	t	romance	en	2026-07-17 06:34:10.325141+00	2026-07-17 06:35:32.764545+00
56dca9da-10ab-43f7-83f4-89acd58f5bb7	mock_google_***@oauth.mock	\N	Google User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 06:35:32.77283+00	2026-07-17 06:35:32.772832+00
b305c5e0-cdac-47e7-a718-c5a4b84f7df0	test@wanderer.com	$2b$12$7sqL7fwkZmBrigD3p6wiyuMFcCfbM5xs4PbuQe9dScgf1TYWS71m2	test	\N	t	\N	\N	basic	\N	\N	f	\N	en	2026-07-17 05:02:23.919151+00	2026-07-17 06:35:53.208175+00
f7533307-789c-4884-b67e-90f1dd184a74	e2e-1784299542244@wanderer.com	$2b$12$NpbYqXD0ENdyM5hRPUiHpepf1wWv0JjEWfis5A2OQzjtMmCN4slyi	e2e-1784299542244	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 06:45:43.319655+00	2026-07-17 06:45:48.509867+00
4c4df553-0ff6-4cbd-b294-12e24cefa68a	finalv2@test.com	$2b$12$ZSP8R4IsIKThhmXfa7NVP.3WdZE8XXaTEe1jnvIvnwqDcOpwSnUX.	finalv2	\N	t	\N	\N	basic	\N	\N	t	romance	en	2026-07-17 06:48:02.441872+00	2026-07-17 06:48:03.236541+00
72e4be91-18a7-4687-b73a-9d890947a139	e2e-1784301824114@wanderer.com	$2b$12$EzcVfDaquRbXhaMGiT/dhOUfIlyzAqU.B7soWG8bjIBHVwUTq9gQy	e2e-1784301824114	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 07:23:45.122431+00	2026-07-17 07:23:45.122434+00
cfcfa1c1-66b5-4334-97b5-c626091beb34	integ1784301197@test.com	$2b$12$X0YFC0BjwhhDLyc64ld41.cwAgTb5afimh7abm20kYOfUG5tNN6k6	integ1784301197	\N	t	\N	\N	basic	\N	\N	t	\N	en	2026-07-17 07:13:17.464938+00	2026-07-17 07:13:17.88376+00
52bc08a5-62a3-4583-8089-f130935b3e5b	e2e-1784301895811@wanderer.com	$2b$12$zgVkNtbh3yf/o1Pe5dGyVeo7T6/Yko8viqR8G1A34YkBJln5v4656	e2e-1784301895811	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 07:24:56.840419+00	2026-07-17 07:25:01.799108+00
c5c5379c-ee36-4cbd-8437-b5041c865a8b	e2e-1784302128132@wanderer.com	$2b$12$ZOA/vfIySq2Ag7m5d2DQwuO0FVxvVt8lcEG1GsCAORBPQo/NZN2Da	e2e-1784302128132	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 07:28:49.135605+00	2026-07-17 07:28:54.123211+00
b7b5ec03-2bcc-4645-9754-bda06a954133	e2e-1784305705864@wanderer.com	$2b$12$7TzLToOnbUYv1malWZEpE.6vgDuUl4HIYGVfPNq01tTTDaXPwvEvi	e2e-1784305705864	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 08:28:26.906926+00	2026-07-17 08:28:32.068153+00
14df719c-0d22-4032-bbac-ae65a6078c07	bossfinal@test.com	$2b$12$f9AuL3uLO6YSILAosyiPhOUZEQlaAzLKzfmcF35KFzak6tRMTEGtC	Boss	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 08:38:45.804219+00	2026-07-17 08:38:45.804224+00
cac23f0a-8424-4ec9-b51e-076ccd031502	mock_google_mock-code-123@oauth.mock	\N	Google User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 08:50:04.900225+00	2026-07-17 08:50:04.900227+00
eaf488f4-6042-4e4a-878d-dcc4a2f4d148	mock_apple_mock-code-123@oauth.mock	\N	Apple User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 08:50:04.905954+00	2026-07-17 08:50:04.905957+00
4cde0b80-2b46-4081-b6af-8e70be92e8e7	integ1b4bdd@test.com	$2b$12$bUmjZWA44yPr7YW2TkP0dO0FDq52ephQUVMWbVVN8JWrym.u561Rm	integ1b4bdd	\N	t	\N	\N	premium	\N	\N	f	\N	en	2026-07-17 08:49:15.499832+00	2026-07-17 08:49:15.835225+00
b30e40e5-943b-4a55-b05b-59e744365acf	mock_wechat_mock-code-123@oauth.mock	\N	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 08:50:04.893814+00	2026-07-17 08:50:04.893818+00
04cd0f99-e09c-4d02-ae3e-77e8d1191e9f	integ8b9371@test.com	$2b$12$7xIuG59BM4fUGsBSso7BzOpaKILbgvx1cllpHppPyETwF075.3eo.	integ8b9371	\N	t	\N	\N	premium	\N	\N	f	\N	en	2026-07-17 08:50:04.625253+00	2026-07-17 08:50:04.968588+00
778dfb6a-46f5-415d-a114-35173f8d8893	integ975738@test.com	$2b$12$b5vh182hnMZcI38rOaUDqudXnyL0AjoOzhpI2ccgabgJmdJW1mgNS	integ975738	\N	t	\N	\N	premium	\N	\N	f	\N	en	2026-07-17 09:03:53.967318+00	2026-07-17 09:03:54.351433+00
d945e90f-6ab4-4c45-8280-9fc98824d923	qa1784307862@test.com	$2b$12$FLNXX1OomZOoj74lxhArjeGr/aHdPbyj/F2z/w/Ge1r6nGyTwTymO	qa1784307862	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 09:04:22.41485+00	2026-07-17 09:04:22.414854+00
26aeb365-1bb2-4f51-9e26-c8fc2dcf2da2	debug_1784307914162@test.com	$2b$12$rERZiPMzMslmcggCGDx3d.u2PknlOV8HQ/ZvXo54re9D6USKnqyz2	debug_1784307914162	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 09:05:14.540827+00	2026-07-17 09:05:14.540833+00
27be36b4-c2ad-4844-9207-40c524e97af5	e2e_1784308015999@test.com	$2b$12$3bKZjnbZwO9KtNEb9ZDr2O79LTTz1K5Z28nzIOLfA/ye7eN5U4P6u	e2e_1784308015999	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 09:06:58.359127+00	2026-07-17 09:06:58.359132+00
47680d40-c99b-4ba0-a44a-ecd335f46dfb	qa-e2e@test.com	$2b$12$8Y4haks01MIYVambROaVT.K9kpyYP5pYJdAPq2Q6ahpPNzYTQiuqy	QA E2E	\N	t	\N	\N	basic	\N	\N	f	\N	en	2026-07-17 09:05:40.45794+00	2026-07-17 09:19:40.787886+00
d03e51b2-280b-45d0-8b4a-63e1fd48c200	e2e_1784307873853@test.com	$2b$12$tBQ.J0uvlakngj1BTzbGDuX1qx0Z8zDLtDF5m.IF9XVbvy.5QYHSK	e2e_1784307873853	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 09:04:36.389621+00	2026-07-17 09:04:36.389625+00
1697729c-6110-45f9-b44c-0811949f0fb7	e2e_1784308110685@test.com	$2b$12$b9oKlux4m5PgCwB7PszSYOoJPbaYY5sBlhmRqgUPECUUEIklJH8Kq	e2e_1784308110685	\N	t	\N	\N	free	\N	\N	t	\N	en	2026-07-17 09:08:34.372854+00	2026-07-17 09:08:43.546374+00
a2ba87f5-51a8-40c7-b84e-d46a48332cf4	e2e_int_1784308195569@test.com	$2b$12$1zpNH0Wh27FQp1gLvTpfnu0L.bUuuXq0YmjDEk8oY.eFg3bBD88Ou	e2e_int_1784308195569	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 09:09:57.816667+00	2026-07-17 09:10:02.633196+00
812a66a0-d73b-49a5-ab90-5b598a9060a2	curltest_1784307978@test.com	$2b$12$4vDTNSWHx00xZa2cGB73/.ouVLTrXQCJQLLbUHkEGrxzRgr0F0ez2	curltest	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 09:06:18.301891+00	2026-07-17 09:06:18.301896+00
b10ecf0e-d237-4db4-8dc2-d3a75ad357d9	mock_google_mock_code_123@oauth.mock	\N	Google User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 09:07:44.853488+00	2026-07-17 09:07:44.853492+00
3e9b3ff7-ccbf-47ba-99ef-1a890bd513c7	qa-test@example.com	$2b$12$pdbCN7wMQEUyZXdKoSjJK.XifrIUeo4YoHptLuB/QiZ1kwk.FhPf2	qa-test	\N	t	\N	\N	free	\N	\N	t	\N	en	2026-07-17 09:06:08.315755+00	2026-07-17 09:07:44.914876+00
5bcd3ab0-458d-4e0c-856a-5436b8c78662	e2e_1784308110686@test.com	$2b$12$Hm9qqNdbQ/7b0taMpVVNHemORIi0jF2NFlj/vDBqs63ZVOrlitHOa	e2e_1784308110686	\N	t	\N	\N	free	\N	\N	t	\N	en	2026-07-17 09:08:34.648219+00	2026-07-17 09:08:43.176143+00
085801f9-68eb-48c2-b54c-1107fea60336	e2e-1784308192066@wanderer.com	$2b$12$dbp4kEcdEGwMeHjNaEzD0OlaXiKHU0Kt4I1zz4o6IAlk6YA4W8Eze	e2e-1784308192066	\N	t	\N	\N	free	\N	\N	t	romance	zh	2026-07-17 09:09:53.064261+00	2026-07-17 09:09:58.181833+00
7e2464bb-9534-4e21-baae-a6fd155c3941	xss@test.com	$2b$12$3FiJzMsN6IQf4ixDbXRXJeB/L8pP/35CV/pNL/lwejL4fxHffG6Fa	<script>alert(1)</script>	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 09:47:26.934551+00	2026-07-17 09:47:26.934555+00
60991d04-c6ad-425a-91f5-4c1001d6ad5c	userA@test.com	$2b$12$nVa6FJAxHVpDqV5BQvIxnOLZyeJEsU6BMeJRi1WB5e8xqpuc03sQC	userA	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 09:51:55.965612+00	2026-07-17 09:51:55.965616+00
b25078d6-c786-49ea-a55a-7af9f6f4a559	userB@test.com	$2b$12$PaJlL.YZ1J7HL4pEsgkiX.2WEb61XvyVtUKGs07C9VNxsWUUP8vZm	userB	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 09:51:56.229483+00	2026-07-17 09:51:56.229487+00
fc23401f-16a3-4277-b7a1-1105643227a0	lockout_test@test.com	$2b$12$SDElb.fWOlXDwNorRU82Bu3WOUVxUuGh4OQFA1LEs/JK7F.Gp.2Te	lockout_test	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:28.154644+00	2026-07-17 10:02:28.154649+00
fb7caf77-efe9-4eb7-8644-40e2ea1a355a	refresh_test@test.com	$2b$12$2LsZU43gWTu6DqZYLN39wems0zTG5lFrXoMXDynghFAwu/z4zuynq	refresh_test	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:29.74351+00	2026-07-17 10:02:29.743514+00
fbb5e757-e3fc-43d6-b77e-6f87dc2ad300	userA_idor@test.com	$2b$12$kgDZwdYaHQXDjf7j3gREl.Xd3zL30dEK6UABUS5dNcxMu/6zVH1Aq	userA_idor	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:30.00628+00	2026-07-17 10:02:30.006285+00
4dfd79a1-6409-4d75-b1da-0c8029fa5a7d	userB_idor@test.com	$2b$12$qR911jFszARHzkyeqU1kJexxKsJHSxDeRoVkcOwIWg08NJOi7AWDi	userB_idor	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:30.268955+00	2026-07-17 10:02:30.268959+00
6e76cf29-a71d-4254-8653-3b229a20b841	oauth_wechat_unique_code_0@mock.local	$2b$12$59OnoKexwLarEkRnapTpFulxjy8JDGMkGyXL4hTo06adlINOJ/LjC	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:30.566966+00	2026-07-17 10:02:30.56697+00
6bdf0762-b72b-4c37-8d27-7a7620028e9c	oauth_wechat_unique_code_1@mock.local	$2b$12$mT3vMZAYHUPU/jAJI1sJiOJpFZ6AhQTmez1v6Jut5XyFhbPVwF9De	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:30.830683+00	2026-07-17 10:02:30.830687+00
504e20ad-4cdf-4ed9-b5fc-bc6cb3088414	oauth_wechat_unique_code_2@mock.local	$2b$12$DSHR8TQLzL0YWQTIz/Y.IeMwPCDyGTqFfVEpytuqC7q9qRJvIX/Ha	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:31.093365+00	2026-07-17 10:02:31.093369+00
c403e517-66af-4d05-98b2-22e88b9fe19f	oauth_wechat_unique_code_3@mock.local	$2b$12$06iRZ3kWVI/kbP0Xt5kDfev1VRJqq3h3Az03maWTa5j2ySsVvyo/S	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:31.355957+00	2026-07-17 10:02:31.355962+00
6371f8d0-3ac6-4f95-9ab1-3759ef65d357	oauth_wechat_unique_code_4@mock.local	$2b$12$pVfOPVvD2/hbH/lrCxRjxOtck2o20MPa/VS/6QE7TmwilpbmOico.	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:31.618482+00	2026-07-17 10:02:31.618486+00
1abe0211-2cc7-4450-8229-6d5af84031c2	oauth_wechat_unique_code_5@mock.local	$2b$12$yRJay8YFtbtuyuoka/OExevd4zHJEfrGs2vEGfIiX9RuW4vXzAi/i	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:31.880808+00	2026-07-17 10:02:31.880811+00
055c07fb-d06a-4338-ad5b-ca9fd503fa59	oauth_wechat_unique_code_6@mock.local	$2b$12$amonq86yMt6LM4IxgPWrYO7WtMPKfZVIgqo7mgPraMocfB3YNXIPO	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:32.144906+00	2026-07-17 10:02:32.14491+00
33127d9c-d74c-43db-b146-aa4079457d0d	oauth_wechat_unique_code_7@mock.local	$2b$12$m6dsDaiyD7VY/w8hJQCZGeg1nCbJyiBfzNqH/E/08rY2FPdFOVr3a	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:32.408147+00	2026-07-17 10:02:32.408151+00
8cfa12ce-cbd4-4982-b5ed-34b69f0a1b04	oauth_wechat_unique_code_8@mock.local	$2b$12$ZanACvSymmu.oVx2ZW.YVOOFPfpzRtK8Bet8aZ1oaNa/jT2u.PMye	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:32.670231+00	2026-07-17 10:02:32.670235+00
092e8d09-04e6-4d32-8088-062a3d0d20d9	oauth_wechat_unique_code_9@mock.local	$2b$12$FesG7YnVmxmmmVxPG2pNNOqSA5K0.Cct5eagh2MhArTuFyL7ATexW	Wechat User	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:32.932149+00	2026-07-17 10:02:32.932153+00
1770fa2f-d0b7-48db-90c5-34978b64285d	refresh_verify@test.com	$2b$12$LggFl5Tb9eRhJX6uqGYTKuX95VOTjnd8iCAbDh73ygN3zfV5Ov7Ym	refresh_verify	\N	t	\N	\N	free	\N	\N	f	\N	en	2026-07-17 10:02:49.276298+00	2026-07-17 10:02:49.276303+00
\.


--
-- Name: achievements achievements_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.achievements
    ADD CONSTRAINT achievements_pkey PRIMARY KEY (id);


--
-- Name: affection_history affection_history_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.affection_history
    ADD CONSTRAINT affection_history_pkey PRIMARY KEY (id);


--
-- Name: affection affection_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.affection
    ADD CONSTRAINT affection_pkey PRIMARY KEY (id);


--
-- Name: affection affection_user_id_character_id_key; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.affection
    ADD CONSTRAINT affection_user_id_character_id_key UNIQUE (user_id, character_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: cg_assets cg_assets_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.cg_assets
    ADD CONSTRAINT cg_assets_pkey PRIMARY KEY (id);


--
-- Name: character_memories character_memories_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.character_memories
    ADD CONSTRAINT character_memories_pkey PRIMARY KEY (id);


--
-- Name: character_sprites character_sprites_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.character_sprites
    ADD CONSTRAINT character_sprites_pkey PRIMARY KEY (id);


--
-- Name: characters characters_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_pkey PRIMARY KEY (id);


--
-- Name: collections collections_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.collections
    ADD CONSTRAINT collections_pkey PRIMARY KEY (id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: daily_checkins daily_checkins_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.daily_checkins
    ADD CONSTRAINT daily_checkins_pkey PRIMARY KEY (id);


--
-- Name: daily_checkins daily_checkins_user_id_date_key; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.daily_checkins
    ADD CONSTRAINT daily_checkins_user_id_date_key UNIQUE (user_id, date);


--
-- Name: daily_tasks daily_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.daily_tasks
    ADD CONSTRAINT daily_tasks_pkey PRIMARY KEY (id);


--
-- Name: daily_tasks daily_tasks_user_id_date_task_type_key; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.daily_tasks
    ADD CONSTRAINT daily_tasks_user_id_date_task_type_key UNIQUE (user_id, date, task_type);


--
-- Name: email_verifications email_verifications_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.email_verifications
    ADD CONSTRAINT email_verifications_pkey PRIMARY KEY (id);


--
-- Name: fragment_transactions fragment_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.fragment_transactions
    ADD CONSTRAINT fragment_transactions_pkey PRIMARY KEY (id);


--
-- Name: fragments fragments_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.fragments
    ADD CONSTRAINT fragments_pkey PRIMARY KEY (id);


--
-- Name: game_progress game_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.game_progress
    ADD CONSTRAINT game_progress_pkey PRIMARY KEY (id);


--
-- Name: game_sessions game_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.game_sessions
    ADD CONSTRAINT game_sessions_pkey PRIMARY KEY (id);


--
-- Name: node_choices node_choices_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.node_choices
    ADD CONSTRAINT node_choices_pkey PRIMARY KEY (id);


--
-- Name: nodes nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_pkey PRIMARY KEY (id);


--
-- Name: oauth_accounts oauth_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.oauth_accounts
    ADD CONSTRAINT oauth_accounts_pkey PRIMARY KEY (id);


--
-- Name: oauth_accounts oauth_accounts_provider_provider_user_id_key; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.oauth_accounts
    ADD CONSTRAINT oauth_accounts_provider_provider_user_id_key UNIQUE (provider, provider_user_id);


--
-- Name: password_resets password_resets_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: purchases purchases_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_pkey PRIMARY KEY (id);


--
-- Name: routes routes_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_pkey PRIMARY KEY (id);


--
-- Name: scenes scenes_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.scenes
    ADD CONSTRAINT scenes_pkey PRIMARY KEY (id);


--
-- Name: scripts scripts_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.scripts
    ADD CONSTRAINT scripts_pkey PRIMARY KEY (id);


--
-- Name: share_cards share_cards_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.share_cards
    ADD CONSTRAINT share_cards_pkey PRIMARY KEY (id);


--
-- Name: streak_records streak_records_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.streak_records
    ADD CONSTRAINT streak_records_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: unlocked_cgs unlocked_cgs_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.unlocked_cgs
    ADD CONSTRAINT unlocked_cgs_pkey PRIMARY KEY (id);


--
-- Name: unlocked_cgs unlocked_cgs_user_id_cg_id_key; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.unlocked_cgs
    ADD CONSTRAINT unlocked_cgs_user_id_cg_id_key UNIQUE (user_id, cg_id);


--
-- Name: unlocked_scripts unlocked_scripts_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.unlocked_scripts
    ADD CONSTRAINT unlocked_scripts_pkey PRIMARY KEY (id);


--
-- Name: unlocked_scripts unlocked_scripts_user_id_script_id_key; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.unlocked_scripts
    ADD CONSTRAINT unlocked_scripts_user_id_script_id_key UNIQUE (user_id, script_id);


--
-- Name: user_preferences user_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_achievements_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_achievements_user_id ON public.achievements USING btree (user_id);


--
-- Name: idx_affection_history_user_char; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_affection_history_user_char ON public.affection_history USING btree (user_id, character_id);


--
-- Name: idx_collections_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_collections_user_id ON public.collections USING btree (user_id);


--
-- Name: idx_comments_post_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_comments_post_id ON public.comments USING btree (post_id);


--
-- Name: idx_comments_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_comments_user_id ON public.comments USING btree (user_id);


--
-- Name: idx_memories_embedding; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_memories_embedding ON public.character_memories USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='100');


--
-- Name: idx_memories_user_char; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_memories_user_char ON public.character_memories USING btree (user_id, character_id);


--
-- Name: idx_oauth_accounts_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_oauth_accounts_user_id ON public.oauth_accounts USING btree (user_id);


--
-- Name: idx_posts_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_posts_user_id ON public.posts USING btree (user_id);


--
-- Name: idx_share_cards_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX idx_share_cards_user_id ON public.share_cards USING btree (user_id);


--
-- Name: idx_users_oauth; Type: INDEX; Schema: public; Owner: isekai
--

CREATE UNIQUE INDEX idx_users_oauth ON public.users USING btree (oauth_provider, oauth_id);


--
-- Name: ix_affection_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_affection_user_id ON public.affection USING btree (user_id);


--
-- Name: ix_cg_assets_route_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_cg_assets_route_id ON public.cg_assets USING btree (route_id);


--
-- Name: ix_cg_assets_script_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_cg_assets_script_id ON public.cg_assets USING btree (script_id);


--
-- Name: ix_character_memories_character_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_character_memories_character_id ON public.character_memories USING btree (character_id);


--
-- Name: ix_character_memories_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_character_memories_user_id ON public.character_memories USING btree (user_id);


--
-- Name: ix_character_sprites_character_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_character_sprites_character_id ON public.character_sprites USING btree (character_id);


--
-- Name: ix_character_sprites_emotion; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_character_sprites_emotion ON public.character_sprites USING btree (emotion);


--
-- Name: ix_characters_script_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_characters_script_id ON public.characters USING btree (script_id);


--
-- Name: ix_daily_checkins_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_daily_checkins_user_id ON public.daily_checkins USING btree (user_id);


--
-- Name: ix_daily_tasks_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_daily_tasks_user_id ON public.daily_tasks USING btree (user_id);


--
-- Name: ix_email_verifications_token; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_email_verifications_token ON public.email_verifications USING btree (token);


--
-- Name: ix_email_verifications_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_email_verifications_user_id ON public.email_verifications USING btree (user_id);


--
-- Name: ix_fragment_transactions_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_fragment_transactions_user_id ON public.fragment_transactions USING btree (user_id);


--
-- Name: ix_fragments_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE UNIQUE INDEX ix_fragments_user_id ON public.fragments USING btree (user_id);


--
-- Name: ix_game_progress_node_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_game_progress_node_id ON public.game_progress USING btree (node_id);


--
-- Name: ix_game_progress_session_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_game_progress_session_id ON public.game_progress USING btree (session_id);


--
-- Name: ix_game_sessions_status; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_game_sessions_status ON public.game_sessions USING btree (status);


--
-- Name: ix_game_sessions_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_game_sessions_user_id ON public.game_sessions USING btree (user_id);


--
-- Name: ix_node_choices_node_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_node_choices_node_id ON public.node_choices USING btree (node_id);


--
-- Name: ix_nodes_node_type; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_nodes_node_type ON public.nodes USING btree (node_type);


--
-- Name: ix_nodes_route_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_nodes_route_id ON public.nodes USING btree (route_id);


--
-- Name: ix_password_resets_token; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_password_resets_token ON public.password_resets USING btree (token);


--
-- Name: ix_password_resets_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_password_resets_user_id ON public.password_resets USING btree (user_id);


--
-- Name: ix_purchases_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_purchases_user_id ON public.purchases USING btree (user_id);


--
-- Name: ix_routes_script_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_routes_script_id ON public.routes USING btree (script_id);


--
-- Name: ix_scenes_script_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_scenes_script_id ON public.scenes USING btree (script_id);


--
-- Name: ix_scripts_slug; Type: INDEX; Schema: public; Owner: isekai
--

CREATE UNIQUE INDEX ix_scripts_slug ON public.scripts USING btree (slug);


--
-- Name: ix_streak_records_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE UNIQUE INDEX ix_streak_records_user_id ON public.streak_records USING btree (user_id);


--
-- Name: ix_subscriptions_status; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_subscriptions_status ON public.subscriptions USING btree (status);


--
-- Name: ix_subscriptions_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_subscriptions_user_id ON public.subscriptions USING btree (user_id);


--
-- Name: ix_unlocked_cgs_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_unlocked_cgs_user_id ON public.unlocked_cgs USING btree (user_id);


--
-- Name: ix_unlocked_scripts_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE INDEX ix_unlocked_scripts_user_id ON public.unlocked_scripts USING btree (user_id);


--
-- Name: ix_user_preferences_user_id; Type: INDEX; Schema: public; Owner: isekai
--

CREATE UNIQUE INDEX ix_user_preferences_user_id ON public.user_preferences USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: isekai
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: achievements achievements_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.achievements
    ADD CONSTRAINT achievements_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: affection affection_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.affection
    ADD CONSTRAINT affection_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id);


--
-- Name: affection_history affection_history_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.affection_history
    ADD CONSTRAINT affection_history_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id);


--
-- Name: affection_history affection_history_source_choice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.affection_history
    ADD CONSTRAINT affection_history_source_choice_id_fkey FOREIGN KEY (source_choice_id) REFERENCES public.node_choices(id);


--
-- Name: affection_history affection_history_source_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.affection_history
    ADD CONSTRAINT affection_history_source_session_id_fkey FOREIGN KEY (source_session_id) REFERENCES public.game_sessions(id);


--
-- Name: affection_history affection_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.affection_history
    ADD CONSTRAINT affection_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: affection affection_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.affection
    ADD CONSTRAINT affection_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: cg_assets cg_assets_route_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.cg_assets
    ADD CONSTRAINT cg_assets_route_id_fkey FOREIGN KEY (route_id) REFERENCES public.routes(id);


--
-- Name: cg_assets cg_assets_script_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.cg_assets
    ADD CONSTRAINT cg_assets_script_id_fkey FOREIGN KEY (script_id) REFERENCES public.scripts(id);


--
-- Name: character_memories character_memories_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.character_memories
    ADD CONSTRAINT character_memories_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id);


--
-- Name: character_memories character_memories_source_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.character_memories
    ADD CONSTRAINT character_memories_source_session_id_fkey FOREIGN KEY (source_session_id) REFERENCES public.game_sessions(id);


--
-- Name: character_memories character_memories_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.character_memories
    ADD CONSTRAINT character_memories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: character_sprites character_sprites_character_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.character_sprites
    ADD CONSTRAINT character_sprites_character_id_fkey FOREIGN KEY (character_id) REFERENCES public.characters(id);


--
-- Name: characters characters_script_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.characters
    ADD CONSTRAINT characters_script_id_fkey FOREIGN KEY (script_id) REFERENCES public.scripts(id);


--
-- Name: collections collections_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.collections
    ADD CONSTRAINT collections_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: comments comments_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: comments comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: daily_checkins daily_checkins_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.daily_checkins
    ADD CONSTRAINT daily_checkins_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: daily_tasks daily_tasks_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.daily_tasks
    ADD CONSTRAINT daily_tasks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: email_verifications email_verifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.email_verifications
    ADD CONSTRAINT email_verifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: fragment_transactions fragment_transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.fragment_transactions
    ADD CONSTRAINT fragment_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: fragments fragments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.fragments
    ADD CONSTRAINT fragments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: game_progress game_progress_choice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.game_progress
    ADD CONSTRAINT game_progress_choice_id_fkey FOREIGN KEY (choice_id) REFERENCES public.node_choices(id);


--
-- Name: game_progress game_progress_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.game_progress
    ADD CONSTRAINT game_progress_node_id_fkey FOREIGN KEY (node_id) REFERENCES public.nodes(id);


--
-- Name: game_progress game_progress_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.game_progress
    ADD CONSTRAINT game_progress_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.game_sessions(id);


--
-- Name: game_sessions game_sessions_current_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.game_sessions
    ADD CONSTRAINT game_sessions_current_node_id_fkey FOREIGN KEY (current_node_id) REFERENCES public.nodes(id);


--
-- Name: game_sessions game_sessions_route_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.game_sessions
    ADD CONSTRAINT game_sessions_route_id_fkey FOREIGN KEY (route_id) REFERENCES public.routes(id);


--
-- Name: game_sessions game_sessions_script_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.game_sessions
    ADD CONSTRAINT game_sessions_script_id_fkey FOREIGN KEY (script_id) REFERENCES public.scripts(id);


--
-- Name: game_sessions game_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.game_sessions
    ADD CONSTRAINT game_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: node_choices node_choices_next_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.node_choices
    ADD CONSTRAINT node_choices_next_node_id_fkey FOREIGN KEY (next_node_id) REFERENCES public.nodes(id);


--
-- Name: node_choices node_choices_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.node_choices
    ADD CONSTRAINT node_choices_node_id_fkey FOREIGN KEY (node_id) REFERENCES public.nodes(id);


--
-- Name: nodes nodes_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.nodes(id);


--
-- Name: nodes nodes_route_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_route_id_fkey FOREIGN KEY (route_id) REFERENCES public.routes(id);


--
-- Name: oauth_accounts oauth_accounts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.oauth_accounts
    ADD CONSTRAINT oauth_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: password_resets password_resets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: posts posts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: purchases purchases_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: routes routes_script_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_script_id_fkey FOREIGN KEY (script_id) REFERENCES public.scripts(id);


--
-- Name: scenes scenes_script_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.scenes
    ADD CONSTRAINT scenes_script_id_fkey FOREIGN KEY (script_id) REFERENCES public.scripts(id);


--
-- Name: share_cards share_cards_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.share_cards
    ADD CONSTRAINT share_cards_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: streak_records streak_records_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.streak_records
    ADD CONSTRAINT streak_records_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: unlocked_cgs unlocked_cgs_cg_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.unlocked_cgs
    ADD CONSTRAINT unlocked_cgs_cg_id_fkey FOREIGN KEY (cg_id) REFERENCES public.cg_assets(id);


--
-- Name: unlocked_cgs unlocked_cgs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.unlocked_cgs
    ADD CONSTRAINT unlocked_cgs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: unlocked_scripts unlocked_scripts_script_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.unlocked_scripts
    ADD CONSTRAINT unlocked_scripts_script_id_fkey FOREIGN KEY (script_id) REFERENCES public.scripts(id);


--
-- Name: unlocked_scripts unlocked_scripts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.unlocked_scripts
    ADD CONSTRAINT unlocked_scripts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_preferences user_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: isekai
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict Uiy6BIPggxkkRgQLXG03H5ego6UebqHAjDmwQWnlXCNms58lE9gi2Px6QwvtMbD

