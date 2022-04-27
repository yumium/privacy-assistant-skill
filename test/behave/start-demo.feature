Feature: Starting demo

	Scenario Outline: Starting the demo
		Given an english speaking user
			When the user says "<start demo>"
			Then "privacy-assistant-skill" should reply with dialog from "startup.intro.dialog"

	Examples: Ways to say start demo
		| start demo |
		| begin demo |
		| start demonstration |
		| begin demonstration |
		| start demo please |