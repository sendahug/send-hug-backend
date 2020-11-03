PGDMP             
        
    x            capstone    12.2    12.2 K    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    24648    capstone    DATABASE     f   CREATE DATABASE capstone WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C';
    DROP DATABASE capstone;
             
   shirbarlev    false            �            1259    24649    alembic_version    TABLE     X   CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);
 #   DROP TABLE public.alembic_version;
       public         heap 
   shirbarlev    false            �            1259    1357933    filters    TABLE     `   CREATE TABLE public.filters (
    id integer NOT NULL,
    filter character varying NOT NULL
);
    DROP TABLE public.filters;
       public         heap    postgres    false            �            1259    1357931    filters_id_seq    SEQUENCE     �   CREATE SEQUENCE public.filters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.filters_id_seq;
       public          postgres    false    218            �           0    0    filters_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.filters_id_seq OWNED BY public.filters.id;
          public          postgres    false    217            �            1259    24652    messages    TABLE     '  CREATE TABLE public.messages (
    id integer NOT NULL,
    from_id integer NOT NULL,
    for_id integer NOT NULL,
    text character varying(480) NOT NULL,
    date timestamp without time zone,
    thread integer NOT NULL,
    for_deleted boolean NOT NULL,
    from_deleted boolean NOT NULL
);
    DROP TABLE public.messages;
       public         heap 
   shirbarlev    false            �            1259    24655    messages_id_seq    SEQUENCE     �   CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.messages_id_seq;
       public       
   shirbarlev    false    203            �           0    0    messages_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;
          public       
   shirbarlev    false    204            �            1259    24762    notifications    TABLE     �   CREATE TABLE public.notifications (
    id integer NOT NULL,
    for_id integer NOT NULL,
    from_id integer NOT NULL,
    type character varying NOT NULL,
    text character varying NOT NULL,
    date timestamp without time zone NOT NULL
);
 !   DROP TABLE public.notifications;
       public         heap 
   shirbarlev    false            �            1259    24760    notifications_id_seq    SEQUENCE     �   CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.notifications_id_seq;
       public       
   shirbarlev    false    214            �           0    0    notifications_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;
          public       
   shirbarlev    false    213            �            1259    24657    posts    TABLE     �   CREATE TABLE public.posts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    text character varying(480) NOT NULL,
    date timestamp without time zone,
    given_hugs integer,
    open_report boolean NOT NULL,
    sent_hugs text
);
    DROP TABLE public.posts;
       public         heap 
   shirbarlev    false            �            1259    24660    posts_id_seq    SEQUENCE     �   CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.posts_id_seq;
       public       
   shirbarlev    false    205            �           0    0    posts_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;
          public       
   shirbarlev    false    206            �            1259    24662    reports    TABLE     J  CREATE TABLE public.reports (
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
    DROP TABLE public.reports;
       public         heap 
   shirbarlev    false            �            1259    24665    reports_id_seq    SEQUENCE     �   CREATE SEQUENCE public.reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.reports_id_seq;
       public       
   shirbarlev    false    207            �           0    0    reports_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;
          public       
   shirbarlev    false    208            �            1259    24783    subscriptions    TABLE     �   CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    "user" integer NOT NULL,
    endpoint character varying NOT NULL,
    subscription_data text NOT NULL
);
 !   DROP TABLE public.subscriptions;
       public         heap 
   shirbarlev    false            �            1259    24781    subscriptions_id_seq    SEQUENCE     �   CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.subscriptions_id_seq;
       public       
   shirbarlev    false    216            �           0    0    subscriptions_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;
          public       
   shirbarlev    false    215            �            1259    24667    threads    TABLE     �   CREATE TABLE public.threads (
    id integer NOT NULL,
    user_1_id integer NOT NULL,
    user_2_id integer NOT NULL,
    user_1_deleted boolean NOT NULL,
    user_2_deleted boolean NOT NULL
);
    DROP TABLE public.threads;
       public         heap 
   shirbarlev    false            �            1259    24670    threads_id_seq    SEQUENCE     �   CREATE SEQUENCE public.threads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.threads_id_seq;
       public       
   shirbarlev    false    209            �           0    0    threads_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.threads_id_seq OWNED BY public.threads.id;
          public       
   shirbarlev    false    210            �            1259    24672    users    TABLE     �  CREATE TABLE public.users (
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
    DROP TABLE public.users;
       public         heap 
   shirbarlev    false            �            1259    24678    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public       
   shirbarlev    false    211            �           0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public       
   shirbarlev    false    212            -           2604    1357936 
   filters id    DEFAULT     h   ALTER TABLE ONLY public.filters ALTER COLUMN id SET DEFAULT nextval('public.filters_id_seq'::regclass);
 9   ALTER TABLE public.filters ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    218    217    218            &           2604    24680    messages id    DEFAULT     j   ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);
 :   ALTER TABLE public.messages ALTER COLUMN id DROP DEFAULT;
       public       
   shirbarlev    false    204    203            +           2604    24765    notifications id    DEFAULT     t   ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);
 ?   ALTER TABLE public.notifications ALTER COLUMN id DROP DEFAULT;
       public       
   shirbarlev    false    214    213    214            '           2604    24681    posts id    DEFAULT     d   ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);
 7   ALTER TABLE public.posts ALTER COLUMN id DROP DEFAULT;
       public       
   shirbarlev    false    206    205            (           2604    24682 
   reports id    DEFAULT     h   ALTER TABLE ONLY public.reports ALTER COLUMN id SET DEFAULT nextval('public.reports_id_seq'::regclass);
 9   ALTER TABLE public.reports ALTER COLUMN id DROP DEFAULT;
       public       
   shirbarlev    false    208    207            ,           2604    24786    subscriptions id    DEFAULT     t   ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);
 ?   ALTER TABLE public.subscriptions ALTER COLUMN id DROP DEFAULT;
       public       
   shirbarlev    false    216    215    216            )           2604    24683 
   threads id    DEFAULT     h   ALTER TABLE ONLY public.threads ALTER COLUMN id SET DEFAULT nextval('public.threads_id_seq'::regclass);
 9   ALTER TABLE public.threads ALTER COLUMN id DROP DEFAULT;
       public       
   shirbarlev    false    210    209            *           2604    24684    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public       
   shirbarlev    false    212    211            �          0    24649    alembic_version 
   TABLE DATA           6   COPY public.alembic_version (version_num) FROM stdin;
    public       
   shirbarlev    false    202   sX       �          0    1357933    filters 
   TABLE DATA           -   COPY public.filters (id, filter) FROM stdin;
    public          postgres    false    218   �X       �          0    24652    messages 
   TABLE DATA           f   COPY public.messages (id, from_id, for_id, text, date, thread, for_deleted, from_deleted) FROM stdin;
    public       
   shirbarlev    false    203   �X       �          0    24762    notifications 
   TABLE DATA           N   COPY public.notifications (id, for_id, from_id, type, text, date) FROM stdin;
    public       
   shirbarlev    false    214   Z       �          0    24657    posts 
   TABLE DATA           \   COPY public.posts (id, user_id, text, date, given_hugs, open_report, sent_hugs) FROM stdin;
    public       
   shirbarlev    false    205   n^       �          0    24662    reports 
   TABLE DATA           o   COPY public.reports (id, type, user_id, post_id, reporter, report_reason, dismissed, closed, date) FROM stdin;
    public       
   shirbarlev    false    207   C`       �          0    24783    subscriptions 
   TABLE DATA           P   COPY public.subscriptions (id, "user", endpoint, subscription_data) FROM stdin;
    public       
   shirbarlev    false    216   �b       �          0    24667    threads 
   TABLE DATA           [   COPY public.threads (id, user_1_id, user_2_id, user_1_deleted, user_2_deleted) FROM stdin;
    public       
   shirbarlev    false    209   d       �          0    24672    users 
   TABLE DATA           �   COPY public.users (id, auth0_id, received_hugs, given_hugs, display_name, login_count, role, blocked, open_report, release_date, last_notifications_read, auto_refresh, push_enabled, refresh_rate) FROM stdin;
    public       
   shirbarlev    false    211   Kd       �           0    0    filters_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.filters_id_seq', 1, false);
          public          postgres    false    217            �           0    0    messages_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.messages_id_seq', 22, true);
          public       
   shirbarlev    false    204            �           0    0    notifications_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.notifications_id_seq', 91, true);
          public       
   shirbarlev    false    213            �           0    0    posts_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.posts_id_seq', 45, true);
          public       
   shirbarlev    false    206            �           0    0    reports_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.reports_id_seq', 44, true);
          public       
   shirbarlev    false    208            �           0    0    subscriptions_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.subscriptions_id_seq', 10, true);
          public       
   shirbarlev    false    215            �           0    0    threads_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.threads_id_seq', 6, true);
          public       
   shirbarlev    false    210            �           0    0    users_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.users_id_seq', 20, true);
          public       
   shirbarlev    false    212            /           2606    24686 #   alembic_version alembic_version_pkc 
   CONSTRAINT     j   ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);
 M   ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
       public         
   shirbarlev    false    202            ?           2606    1357941    filters filters_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.filters
    ADD CONSTRAINT filters_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.filters DROP CONSTRAINT filters_pkey;
       public            postgres    false    218            1           2606    24688    messages messages_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.messages DROP CONSTRAINT messages_pkey;
       public         
   shirbarlev    false    203            ;           2606    24770     notifications notifications_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.notifications DROP CONSTRAINT notifications_pkey;
       public         
   shirbarlev    false    214            3           2606    24690    posts posts_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_pkey;
       public         
   shirbarlev    false    205            5           2606    24692    reports reports_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.reports DROP CONSTRAINT reports_pkey;
       public         
   shirbarlev    false    207            =           2606    24791     subscriptions subscriptions_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.subscriptions DROP CONSTRAINT subscriptions_pkey;
       public         
   shirbarlev    false    216            7           2606    24694    threads threads_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.threads
    ADD CONSTRAINT threads_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.threads DROP CONSTRAINT threads_pkey;
       public         
   shirbarlev    false    209            9           2606    24696    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public         
   shirbarlev    false    211            @           2606    24697    messages messages_for_id_fkey    FK CONSTRAINT     {   ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_for_id_fkey FOREIGN KEY (for_id) REFERENCES public.users(id);
 G   ALTER TABLE ONLY public.messages DROP CONSTRAINT messages_for_id_fkey;
       public       
   shirbarlev    false    203    3129    211            A           2606    24702    messages messages_from_id_fkey    FK CONSTRAINT     }   ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_from_id_fkey FOREIGN KEY (from_id) REFERENCES public.users(id);
 H   ALTER TABLE ONLY public.messages DROP CONSTRAINT messages_from_id_fkey;
       public       
   shirbarlev    false    211    3129    203            B           2606    24707    messages messages_thread_fkey    FK CONSTRAINT     }   ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_thread_fkey FOREIGN KEY (thread) REFERENCES public.threads(id);
 G   ALTER TABLE ONLY public.messages DROP CONSTRAINT messages_thread_fkey;
       public       
   shirbarlev    false    209    203    3127            I           2606    24771 '   notifications notifications_for_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_for_id_fkey FOREIGN KEY (for_id) REFERENCES public.users(id);
 Q   ALTER TABLE ONLY public.notifications DROP CONSTRAINT notifications_for_id_fkey;
       public       
   shirbarlev    false    211    214    3129            J           2606    24776 (   notifications notifications_from_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_from_id_fkey FOREIGN KEY (from_id) REFERENCES public.users(id);
 R   ALTER TABLE ONLY public.notifications DROP CONSTRAINT notifications_from_id_fkey;
       public       
   shirbarlev    false    214    211    3129            C           2606    24712    posts posts_user_id_fkey    FK CONSTRAINT     w   ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
 B   ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_user_id_fkey;
       public       
   shirbarlev    false    3129    205    211            D           2606    24717    reports reports_post_id_fkey    FK CONSTRAINT     {   ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);
 F   ALTER TABLE ONLY public.reports DROP CONSTRAINT reports_post_id_fkey;
       public       
   shirbarlev    false    3123    205    207            E           2606    24722    reports reports_reporter_fkey    FK CONSTRAINT     }   ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_reporter_fkey FOREIGN KEY (reporter) REFERENCES public.users(id);
 G   ALTER TABLE ONLY public.reports DROP CONSTRAINT reports_reporter_fkey;
       public       
   shirbarlev    false    211    3129    207            F           2606    24727    reports reports_user_id_fkey    FK CONSTRAINT     {   ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
 F   ALTER TABLE ONLY public.reports DROP CONSTRAINT reports_user_id_fkey;
       public       
   shirbarlev    false    211    3129    207            K           2606    24792 %   subscriptions subscriptions_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_fkey FOREIGN KEY ("user") REFERENCES public.users(id);
 O   ALTER TABLE ONLY public.subscriptions DROP CONSTRAINT subscriptions_user_fkey;
       public       
   shirbarlev    false    3129    216    211            G           2606    24732    threads threads_user_1_id_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.threads
    ADD CONSTRAINT threads_user_1_id_fkey FOREIGN KEY (user_1_id) REFERENCES public.users(id);
 H   ALTER TABLE ONLY public.threads DROP CONSTRAINT threads_user_1_id_fkey;
       public       
   shirbarlev    false    209    3129    211            H           2606    24737    threads threads_user_2_id_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.threads
    ADD CONSTRAINT threads_user_2_id_fkey FOREIGN KEY (user_2_id) REFERENCES public.users(id);
 H   ALTER TABLE ONLY public.threads DROP CONSTRAINT threads_user_2_id_fkey;
       public       
   shirbarlev    false    209    211    3129            �      x�3ML446J�4�HM����� ,�      �      x������ � �      �   U  x����N�0���S�;,���m"�\x$.�e��[К���8�����Cr�~��ojT)�1�Gx�C�ۇ{ ���� �Ї���]�7�;�B�_�~?�t��؇A+F�5Vkf�����h+��Ԯ��ZՆ~>��W�M�����Aw*�ʢ��Ԇc��-zr��|(�P*3��7�.�\��׌��Z��S���|ۍ���"Bo���6�t'>��&u��M��s���9��Y��Y��)�TYm�>J��<�R`=Z]���;���.BV���J���.�E�ls��r��X�k���e�%yb�d�x���\-(���x���o�'.� K��47�L>�(� �t�)      �   ?  x���;n,9Ecsހ�%�N�d�7�K��.����%�8PutI�|8>�������?��~����g������ק��q���3$/�Q�Iv�x�Ԍ(�#D�23�C)��+|x��Q �yY��h!��F��0ZGH�Kװ�Au��e|	V�		�1~)��1+���"������$h�n�.T@ v��\2I�f�v٘��"9p��c#���H�ԧ@��BƊųm- ����K�P��f^RcM�~��7��9�g���n=�����@��$�zp3m���E���F��0l�	��&�;ħ1��7���*0ҭ�����ˍ�D���2�VPGO4@DU��)v�v�At`{bzMl�N�O�PFxvl������l9W3;Lg#�ؑ�;��`CW��΃fP ���,,cd;^�q��v�A���U�l���1i�U�϶���h;:W�b��O&._�-�P�����R4_����B\���HD��7g��z���:�̓|��D�:�9����Mу�dt!�z�`V�95W��y~ȖA��2\|)j���Š��
�S����A�jq0j�����fB��@�Ϗ�LH'�΃'�GhL]���y�b<�!�(v<�[#w���;{����8s������0�a�]<�.�0.kR�<�a����i�z��G{��D�v<��R�cHέ7�q�SFs�����R�0[��v�kBƜ�[��h%K�r�����J8�#vr��7�u����j�`�)�b~��jp3�^0&X)�,��'>�.B�e�x`�"ĥ��1����|i4�20r���:<�'�}_�Q(\劦}�����t:M?{60>fD�u� �	���-����L �#g(�%�y�TO�)��s1}���8�B�D���v�قu�ⷥ^_�}il���+��ԗd��)��D5Xo5�2~*���2[A�m4s�(j�5
���o����+借h
�m�\JI�Kp�y���q�)jaN��6~��RO���ަ����DPj|��������D+�E��+�0���*�_o���a���,�{���4<�      �   �  x�u��r� ���)��)�e$!0�,�t��t����f����n���������g�^G���	������;E�^뎂�K����Fl5��694䜊+�7X�C����6� Y6��GY��U+�O�]�t�$���?��5gQ���!$)q`�`�*�O��<��<g�1N���J��(�0��[/�Ć�E�����8YH.�r{�-������>9� �>b-鷡�7:�M �0��J�J�ф���0��bŗ�`ŅX@�z� ��PVy�?Y�pA�"'�6�Q.2�����~lqA��`���3ݮ�u'�{&c��؊�N���z[q�u*�������8--��KX���|���{ G��}5�֟� �}Y��[.l��;�.ʻ�[Y�QմC�y,���������,�p�%<��@��Y�A	F0(�~����H �8��w����/�[�9      �   W  x����nSA���O��5���7`H���JMJ�Qx~Τ���M����}fl>�>?��Lu�����j���v���x��=?ힷw��t�O����nTWb�J��CT�?"Wix�I`B������Y�~���FN)�/ְ��P����ȗ�ݏ�k��Bm�,V)^x��>�7O5S�����S����]�km�^.��-	�e�t2��RYEB~3e���R	��=����LHs4C��"`+s�"zR;P!p(Jr)�gD�WQ@���]@�VH��X~�l֏���s�Gk��$㍘����%C /��������17\+fX������t���BS�+��a����ҒI�������5��)�F�ǒQ��ً�&�5&�1���l���/�g�F@B7�R�tϬ���E)�cpf^���B�"���e���Q���mL�\�e
�1A��	�न�:C��/g�dqћ�5�0��^}<��OlF����|��-��^2����G+�ʑR�g%\ލ�$+G���X���n,��̮�\Ob6������LN�k暌�Nr��0Τ��h3�W����V��0V�+�����7dz�M      �   T  x�ՏIr�@ E�r
�u�)N�C16D�Re!�2�LZ�=�[d���7t��(�|��_ܨ�%�G��y�M�7��$�}���L�\��sóH�(CÎ�R�AC7J�֟&�V�`H|�sD�"����#�7ۑb)��i����9f��L����;dl#p)�>�ͪ�F��a�FX=�����_$��Γm��$�v�e�s
��eI�7���"��%�-��&oדMG�)�ߩKx?A�g���e�a	��j�+sd)�hJ��%5�X]ͅ����|�2&3����nu�B	F�٩N�귫zؿ-����(�����9�d�H(ы���׋��1�޽�      �   -   x�3�4�4�4.# m
fY&`��%T�(b�Yd��qqq �!�      �   �   x�u�Kn�0��)r�ԇ��dcY�E�qv9|e������H`摑��z�˕\5�C�A ؈z��@L�GY�!�)߮�T�;�W'��T�b�1�����ZoL�`�m��Ck�z����03�V�
[?��'��(v�y���#���]E
�c%�<y!��y\�K"���ۃ��ȥ��H��Y�k����ْ��ڃ2z����<H8���fp�����ۅ]D���e�����2��寰��/��j`     