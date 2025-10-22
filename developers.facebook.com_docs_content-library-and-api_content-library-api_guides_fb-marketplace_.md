Text file: developers.facebook.com_docs_content-library-and-api_content-library-api_guides_fb-marketplace_.md
Latest content with line numbers:
1	# Facebook Marketplace - Meta Content Library and API
2	
3	**URL:** https://developers.facebook.com/docs/content-library-and-api/content-library-api/guides/fb-marketplace/
4	
5	---
6	
7	Docs
8	Tools
9	Support
10	Log In
11	Docs
12	Meta Content Library and API
13	Content Library API
14	Guides
15	Facebook Marketplace
16	Meta Content Library and API
17	Get access
18	Quick links
19	Content Library
20	Content Library API
21	Overview
22	Getting started
23	Guides
24	Facebook Pages
25	Facebook groups
26	Facebook events
27	Facebook profiles
28	Facebook posts
29	Facebook Marketplace
30	Facebook Fundraisers
31	Facebook donations
32	Facebook comments
33	Instagram accounts
34	Instagram posts
35	Instagram Fundraisers
36	Instagram channels
37	Instagram channel messages
38	Instagram comments
39	Bulk comments
40	ID-based retrieval
41	Search guide
42	Advanced search
43	Rate limiting
44	Data deletion
45	Appendix
46	Support
47	Disclosures and disclaimers
48	Citations
49	Changelog
50	On This Page
51	Guide to Facebook Marketplace data
52	
53	You can perform Facebook Marketplace searches by calling the Meta Content Library API client get() method with the search/facebook_marketplace_listings path. This document describes the parameters, and shows how to perform basic queries using the method.
54	
55	All of the examples in this document are taken from a Secure Research Environment use case and assume you have created a Jupyter notebook and a client object. See Getting started to learn more.
56	
57	See Data dictionary for detailed information about the fields that are available on a Facebook Marketplace node.
58	
59	Parameters
60	Parameter	Type	Description
61	
62	
63	Q
64	Optional
65	
66		
67	
68	String
69	
70		
71	
72	Keyword(s) to search for. Searches listing listing_details.title and description fields. See Advanced search guidelines for information about how multiple keyword searches with Boolean operators are handled.
73	
74	
75	
76	
77	CATEGORIES
78	Optional
79	
80		
81	
82	List
83	
84		
85	
86	Comma-separated list of listing category names to include in the search. Keywords can be used to match categories. Categories are visible in the Meta Content Library UI and in the Facebook Marketplace mobile app.
87	
88	
89	
90	
91	FIELDS
92	Optional
93	
94		
95	
96	List
97	
98		
99	
100	Comma-separated list of Marketplace listing fields you want included in search results. See Data dictionary for descriptions of all available fields.
101	
102	
103	
104	
105	CONTENT_TYPES
106	Optional
107	
108		
109	
110	List
111	
112		
113	
114	Comma-separated list of content types to be included in the search results. Available content types are photos and videos (which includes photos).
115	
116	
117	
118	
119	LISTING_COUNTRIES
120	Optional
121	
122		
123	
124	List
125	
126		
127	
128	Comma-separated list of countries to include. Takes ISO Alpha-2 Country Code in 2-letter uppercase format.
129	
130	
131	
132	
133	SORT
134	Optional
135	
136		
137	
138	Enum
139	
140		
141	
142	Sort mode specifying the order in which listings are returned (only available for synchronous searches). Available options:
143	
144	most_to_least_views: Listings are returned based on the number of views (most views first).
145	newest_to_oldest: Listings are returned in reverse chronological order (newest first).
146	oldest_to_newest: Listings are returned in chronological order (oldest first).
147	
148	Additional available options when the listing_countries parameter specifies only one country:
149	
150	highest_to_lowest_price: Listings are returned based on the price (highest price first).
151	lowest_to_highest_price: Listings are returned based on the price (lowest price first).
152	
153	Default: most_to_least_views
154	
155	
156	
157	
158	PRICE_MIN Optional
159	
160		
161	
162	Integer
163	
164		
165	
166	Minimum price for the search in the currency of the listing country when only a single listing country is included. Not valid when the listing_countries parameter specifies multiple countries or when the listing_countries parameter is omitted.
167	
168	
169	
170	
171	PRICE_MAX
172	Optional
173	
174		
175	
176	Integer
177	
178		
179	
180	Maximum price for the search in the currency of the listing country when only a single listing country is included. Not valid when the listing_countries parameter specifies multiple countries or when the listing_countries parameter is omitted.
181	
182	
183	
184	
185	VIEWS_BUCKET_START
186	Optional
187	
188		
189	
190	Integer
191	
192		
193	
194	Marketplace listings with view counts larger than or equal to this number match the search criteria. Range is from 0 to the maximum of more than 100 million. Used with views_bucket_end to define a range.
195	
196	
197	
198	
199	Views are the number of times the listing was on screen, not including times it appeared on the seller’s screen. View counts for Marketplace listings are refreshed every 2-3 days.
200	
201	
202	
203	
204	VIEWS_BUCKET_END Optional
205	
206		
207	
208	Integer
209	
210		
211	
212	Marketplace listings with view counts smaller than or equal to this number match the search criteria. Range is from 0 to the maximum of more than 100 million. Used with views_bucket_start to define a range.
213	
214	
215	
216	
217	Views are the number of times the listing was on screen, not including times it appeared on the seller’s screen. View counts for Marketplace listings are refreshed every 2-3 days.
218	
219	
220	
221	
222	SINCE
223	Optional
224	
225		
226	
227	String or Integer
228	
229		
230	
231	Date in YYYY-MM-DD (date only) or UNIX timestamp (translates to a date and time to the second) format. Marketplace listings created on or after this date or timestamp are returned (used with UNTIL to define a time range). SINCE and UNTIL are based on UTC time zone, regardless of the local time zone of the seller who made the listing.
232	
233	If both SINCE and UNTIL are included, the search includes the time range defined by those values.
234	If SINCE is included and UNTIL is omitted, the search includes the SINCE time through the present time.
235	If SINCE is omitted and UNTIL is included, the search goes from the beginning of Facebook time through the UNTIL time.
236	If SINCE and UNTIL are both omitted, the search goes from the beginning of Facebook time to the present time.
237	If SINCE and UNTIL are the same UNIX timestamp, the search includes the SINCE time through the SINCE time plus one hour.
238	If SINCE and UNTIL are the same date (YYYY-MM-DD), the search includes the SINCE date through the SINCE date plus one day.
239	
240	
241	
242	UNTIL
243	Optional
244	
245		
246	
247	String or Integer
248	
249		
250	
251	Date in YYYY-MM-DD (date only) or UNIX timestamp (translates to a date and time to the second) format. Marketplace listings created on or before this date or timestamp are returned (used with SINCE to define a time range). SINCE and UNTIL are based on UTC time zone, regardless of the local time zone of the seller who made the listing.
252	
253	If both SINCE and UNTIL are included, the search includes the time range defined by those values.
254	If SINCE is included and UNTIL is omitted, the search includes the SINCE time through the present time.
255	If SINCE is omitted and UNTIL is included, the search goes from the beginning of Facebook time through the UNTIL time.
256	If SINCE and UNTIL are both omitted, the search goes from the beginning of Facebook time to the present time.
257	If SINCE and UNTIL are the same UNIX timestamp, the search includes the SINCE time through the SINCE time plus one hour.
258	If SINCE and UNTIL are the same date (YYYY-MM-DD), the search includes the SINCE date through the SINCE date plus one day.
259	Sample queries
260	Search for listings by keyword
261	
262	To search for all public listings on Facebook Marketplace that contain specific keywords, use the q parameter. See Advanced search guidelines for information about how multiple keyword searches are handled.
263	
264	RPython
265	library(reticulate)
266	client <- import("metacontentlibraryapi")$MetaContentLibraryAPIClient
267	
268	client$set_default_version(client$LATEST_VERSION)
269	
270	response <- client$get(path="search/facebook_marketplace_listings", params=list("q"="rentals"))
271	jsonlite::fromJSON(response$text, flatten=TRUE) # Display first page
272	Search for listings by price
273	
274	Use the price_max parameter to specify the highest price you want included in search results. Remember that this parameter is only valid when a single country is specified using the listing_countries parameter.
275	
276	RPython
277	response <- client$get(path="search/facebook_marketplace_listings", params=list("listing_countries"="US", "price_max"="10000", "q"="rentals"))
278	jsonlite::fromJSON(response$text, flatten=TRUE) # Display first page
279	Search for listings by categories
280	
281	To search for listings in specific categories, use the categories parameter to specify the list of categories to include in the results.
282	
283	RPython
284	response <- client$get(path="search/facebook_marketplace_listings", params=list("categories"="Clothing, Shoes & Accessories,Rentals,Books, Movies & Music", "q"="rentals"))
285	jsonlite::fromJSON(response$text, flatten=TRUE) # Display first page
286	Including multimedia in search results
287	
288	Multimedia in responses to queries on Secure Research Environment include the type of media (photo, video), a Meta Content Library ID, the duration and any user tags. You can get the URL for the media by querying for ”fields”=”multimedia{url}”.
289	
290	Multimedia is not included in responses to queries in third-party cleanrooms by default. Third-party cleanroom users can get multimedia by querying for ”fields”=”multimedia”. In addition to the type, Meta Content Library ID, duration and user tags, the URL is included in multimedia responses in third-party cleanrooms. Multimedia is available in posts from Facebook Pages, profiles, groups, and events.
291	
292	Include the keyword multimedia in your query (fields parameter) on third-party cleanrooms, because multimedia is not included by default.
293	
294	Include the keyword multimedia{url} in your query (fields parameter) on Secure Research Environment to obtain the media URL, because the URL is not included by default.
295	
296	To display multimedia in Secure Research Environment use display_media().
297	
298	The number of calls allowed that include multimedia is controlled by a multimedia query budget specific to the third-party cleanroom environment. See Rate limiting and query budgeting for multimedia for more information. To download multimedia content, use download_multimedia_by_content_ids() with a list of known content IDs. See Guide to ID-based retrieval for information on how to retrieve content IDs.
299	
300	RPython
301	# Load required libraries
302	library(reticulate)
303	meta_content_library_api <- import("metacontentlibraryapi")
304	utils <- meta_content_library_api$MetaContentLibraryAPIMultimediaUtils
305	# Provide a comma-separated list of content ids as strings
306	ids_to_download <- c("553170087752425", "681021651202495")
307	# Download the multimedia content
308	utils$download_multimedia_by_content_ids(ids_to_download)
309	# The file path is displayed when the above command is run
310	utils$display_media(<FILE_PATH>)
311	Learn more
312	Advanced search guidelines
313	Data dictionary
314	Build with Meta
315	AI
316	Meta Horizon OS
317	Social technologies
318	Wearables
319	News
320	Meta for Developers
321	Blog
322	Success stories
323	Support
324	Developer support
325	Bug tool
326	Platform status
327	Developer community forum
328	Report an incident
329	Terms and policies
330	Responsible platform initiatives
331	Platform terms
332	Developer policies
333	© 2025 Meta
334	About
335	Careers
336	Privacy Policy
337	Cookies
338	Terms
339	English (US)
340	Bahasa Indonesia
341	Deutsch
342	Español
343	Español (España)
344	Français (France)
345	Italiano
346	Português (Brasil)
347	Tiếng Việt
348	Русский
349	العربية
350	ภาษาไทย
351	한국어
352	中文(香港)
353	中文(台灣)
354	中文(简体)
355	日本語
356	English (US)