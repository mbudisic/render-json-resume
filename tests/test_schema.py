"""Tests for JSON Resume schema validation."""

import pytest
from pydantic import ValidationError

from resume_forge.schema import (
    Resume,
    Basics,
    Work,
    Education,
    Skill,
    Project,
    Profile,
    Location,
    Certificate,
    Award,
    Publication,
    Volunteer,
    Language,
    Interest,
    Reference,
)


class TestResumeSchemaValidation:
    """Test that the schema correctly validates JSON Resume data."""
    
    def test_empty_resume_is_valid(self) -> None:
        """An empty resume with no sections should be valid per JSON Resume spec."""
        resume = Resume()
        assert resume.basics is None
        assert resume.work == []
        assert resume.education == []
    
    def test_minimal_resume_with_name_only(self) -> None:
        """A resume with just a name should be valid."""
        resume = Resume(basics=Basics(name="John Doe"))
        assert resume.basics.name == "John Doe"
    
    def test_complete_basics_section(self) -> None:
        """Test that all basics fields are properly parsed."""
        basics = Basics(
            name="Jane Smith",
            label="Software Engineer",
            email="jane@example.com",
            phone="+1-555-1234",
            url="https://janesmith.dev",
            summary="Experienced developer",
            location=Location(
                city="San Francisco",
                region="California",
                countryCode="US"
            ),
            profiles=[
                Profile(network="GitHub", username="janesmith", url="https://github.com/janesmith")
            ]
        )
        resume = Resume(basics=basics)
        
        assert resume.basics.name == "Jane Smith"
        assert resume.basics.location.city == "San Francisco"
        assert len(resume.basics.profiles) == 1
        assert resume.basics.profiles[0].network == "GitHub"
    
    def test_work_experience_with_highlights(self) -> None:
        """Work entries should support highlights list."""
        work = Work(
            name="Tech Corp",
            position="Senior Developer",
            startDate="2020-01-01",
            endDate="2023-12-31",
            summary="Led development team",
            highlights=["Built scalable systems", "Mentored juniors"]
        )
        resume = Resume(work=[work])
        
        assert len(resume.work) == 1
        assert len(resume.work[0].highlights) == 2
        assert "Built scalable systems" in resume.work[0].highlights
    
    def test_current_job_without_end_date(self) -> None:
        """A current job should not require an end date."""
        work = Work(
            name="Current Employer",
            position="Developer",
            startDate="2023-01-01"
        )
        assert work.endDate is None
    
    def test_education_with_courses(self) -> None:
        """Education entries should support a courses list."""
        edu = Education(
            institution="MIT",
            area="Computer Science",
            studyType="Bachelor",
            startDate="2010-09-01",
            endDate="2014-05-15",
            score="3.9",
            courses=["Algorithms", "Data Structures", "Operating Systems"]
        )
        resume = Resume(education=[edu])
        
        assert len(resume.education[0].courses) == 3
        assert "Algorithms" in resume.education[0].courses
    
    def test_skills_with_keywords(self) -> None:
        """Skills should support keywords and proficiency levels."""
        skill = Skill(
            name="Programming",
            level="Expert",
            keywords=["Python", "TypeScript", "Go"]
        )
        resume = Resume(skills=[skill])
        
        assert resume.skills[0].level == "Expert"
        assert "Python" in resume.skills[0].keywords
    
    def test_project_with_url(self) -> None:
        """Projects should support URLs for linking to the project."""
        project = Project(
            name="Open Source Tool",
            description="A helpful CLI tool",
            url="https://github.com/user/project",
            startDate="2022-01-01",
            highlights=["10k+ stars", "Used by Fortune 500"]
        )
        resume = Resume(projects=[project])
        
        assert resume.projects[0].url == "https://github.com/user/project"
    
    def test_multiple_profiles_supported(self) -> None:
        """Multiple social profiles should be supported."""
        profiles = [
            Profile(network="GitHub", username="johndoe"),
            Profile(network="LinkedIn", username="johndoe"),
            Profile(network="Twitter", username="johndoe"),
        ]
        basics = Basics(name="John Doe", profiles=profiles)
        
        assert len(basics.profiles) == 3
        networks = [p.network for p in basics.profiles]
        assert "GitHub" in networks
        assert "LinkedIn" in networks
    
    def test_all_resume_sections_can_coexist(self) -> None:
        """A full resume with all sections should be valid."""
        resume = Resume(
            basics=Basics(name="Full Resume Person"),
            work=[Work(name="Company", position="Role")],
            education=[Education(institution="University", area="Science")],
            skills=[Skill(name="Python")],
            projects=[Project(name="My Project")],
            certificates=[Certificate(name="AWS Certified")],
            awards=[Award(title="Best Employee")],
            publications=[Publication(name="Research Paper")],
            volunteer=[Volunteer(organization="Charity")],
            languages=[Language(language="English", fluency="Native")],
            interests=[Interest(name="Open Source")],
            references=[Reference(name="Jane Smith")]
        )
        
        assert resume.basics.name == "Full Resume Person"
        assert len(resume.work) == 1
        assert len(resume.education) == 1
        assert len(resume.skills) == 1
        assert len(resume.projects) == 1
        assert len(resume.certificates) == 1
        assert len(resume.awards) == 1
        assert len(resume.publications) == 1
        assert len(resume.volunteer) == 1
        assert len(resume.languages) == 1
        assert len(resume.interests) == 1
        assert len(resume.references) == 1


class TestSchemaFromDict:
    """Test parsing resume data from dictionaries (simulating JSON input)."""
    
    def test_parse_minimal_json(self) -> None:
        """Should parse a minimal JSON Resume dict."""
        data = {
            "basics": {
                "name": "Test User"
            }
        }
        resume = Resume.model_validate(data)
        assert resume.basics.name == "Test User"
    
    def test_parse_work_section(self) -> None:
        """Should correctly parse work experience from dict."""
        data = {
            "work": [
                {
                    "name": "Acme Inc",
                    "position": "Developer",
                    "startDate": "2020-01-15",
                    "highlights": ["Feature A", "Feature B"]
                }
            ]
        }
        resume = Resume.model_validate(data)
        assert resume.work[0].name == "Acme Inc"
        assert len(resume.work[0].highlights) == 2
    
    def test_parse_nested_location(self) -> None:
        """Should correctly parse nested location object."""
        data = {
            "basics": {
                "name": "Test",
                "location": {
                    "city": "Berlin",
                    "countryCode": "DE"
                }
            }
        }
        resume = Resume.model_validate(data)
        assert resume.basics.location.city == "Berlin"
        assert resume.basics.location.countryCode == "DE"
    
    def test_unknown_fields_are_ignored(self) -> None:
        """Unknown fields should not cause validation errors."""
        data = {
            "basics": {
                "name": "Test",
                "unknown_field": "should be ignored"
            }
        }
        resume = Resume.model_validate(data)
        assert resume.basics.name == "Test"
    
    def test_empty_arrays_are_valid(self) -> None:
        """Empty arrays for list fields should be valid."""
        data = {
            "work": [],
            "education": [],
            "skills": []
        }
        resume = Resume.model_validate(data)
        assert resume.work == []
        assert resume.education == []
        assert resume.skills == []
