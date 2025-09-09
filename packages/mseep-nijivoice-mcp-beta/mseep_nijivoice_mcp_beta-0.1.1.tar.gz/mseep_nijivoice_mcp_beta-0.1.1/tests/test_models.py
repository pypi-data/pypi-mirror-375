"""Test suite for models.py."""
import pytest
from pydantic import ValidationError

from nijivoice.models import (
    RecommendedParameters,
    VoiceStyle,
    VoiceActor,
    VoiceGenerationRequest,
    Balance
)


class TestRecommendedParameters:
    """Tests for RecommendedParameters model."""

    def test_create_recommended_parameters(self):
        """Test creating RecommendedParameters with default values."""
        params = RecommendedParameters()
        assert params.emotional_level == 1.0
        assert params.sound_duration == 1.0

    def test_create_with_values(self):
        """Test creating RecommendedParameters with values."""
        params = RecommendedParameters(
            emotional_level=0.8,
            sound_duration=1.2
        )
        assert params.emotional_level == 0.8
        assert params.sound_duration == 1.2

    def test_create_with_aliases(self):
        """Test creating RecommendedParameters using alias names."""
        params = RecommendedParameters(
            emotionalLevel=0.8,
            soundDuration=1.2
        )
        assert params.emotional_level == 0.8
        assert params.sound_duration == 1.2

    def test_ignore_extra_fields(self):
        """Test that extra fields are ignored."""
        params = RecommendedParameters(
            emotional_level=0.8,
            sound_duration=1.2,
            extra_field="should be ignored"
        )
        assert not hasattr(params, "extra_field")


class TestVoiceStyle:
    """Tests for VoiceStyle model."""

    def test_create_voice_style(self):
        """Test creating VoiceStyle."""
        style = VoiceStyle(id=1, style="normal")
        assert style.id == 1
        assert style.style == "normal"

    def test_voice_style_validation(self):
        """Test VoiceStyle validation."""
        # Missing required field should raise ValidationError
        with pytest.raises(ValidationError):
            VoiceStyle(style="normal")  # Missing id
        
        with pytest.raises(ValidationError):
            VoiceStyle(id=1)  # Missing style


class TestVoiceActor:
    """Tests for VoiceActor model."""

    def test_create_voice_actor_minimal(self):
        """Test creating VoiceActor with minimal required fields."""
        actor = VoiceActor(id="actor-1", name="Test Actor")
        assert actor.id == "actor-1"
        assert actor.name == "Test Actor"
        assert actor.description == ""  # Default value
        assert actor.gender is None
        assert actor.age is None

    def test_create_voice_actor_full(self):
        """Test creating VoiceActor with all fields."""
        actor = VoiceActor(
            id="actor-1",
            name="Test Actor",
            name_reading="テストアクター",
            age=25,
            gender="Female",
            birth_month=7,
            birth_day=15,
            description="Test description",
            small_image_url="https://example.com/small.jpg",
            medium_image_url="https://example.com/medium.jpg",
            large_image_url="https://example.com/large.jpg",
            sample_voice_url="https://example.com/sample.mp3",
            sample_script="こんにちは",
            recommended_voice_speed=1.2,
            recommended_emotional_level=0.8,
            recommended_sound_duration=1.0,
            recommended_parameters=RecommendedParameters(
                emotional_level=0.8,
                sound_duration=1.0
            ),
            voice_styles=[
                VoiceStyle(id=1, style="normal"),
                VoiceStyle(id=2, style="happy")
            ]
        )
        
        assert actor.id == "actor-1"
        assert actor.name == "Test Actor"
        assert actor.name_reading == "テストアクター"
        assert actor.age == 25
        assert actor.gender == "Female"
        assert actor.birth_month == 7
        assert actor.birth_day == 15
        assert actor.description == "Test description"
        assert actor.small_image_url == "https://example.com/small.jpg"
        assert actor.medium_image_url == "https://example.com/medium.jpg"
        assert actor.large_image_url == "https://example.com/large.jpg"
        assert actor.sample_voice_url == "https://example.com/sample.mp3"
        assert actor.sample_script == "こんにちは"
        assert actor.recommended_voice_speed == 1.2
        assert actor.recommended_emotional_level == 0.8
        assert actor.recommended_sound_duration == 1.0
        assert isinstance(actor.recommended_parameters, RecommendedParameters)
        assert len(actor.voice_styles) == 2
        assert actor.voice_styles[0].id == 1
        assert actor.voice_styles[0].style == "normal"

    def test_create_with_aliases(self):
        """Test creating VoiceActor using alias names."""
        actor = VoiceActor(
            id="actor-1",
            name="Test Actor",
            nameReading="テストアクター",
            birthMonth=7,
            birthDay=15,
            smallImageUrl="https://example.com/small.jpg",
            mediumImageUrl="https://example.com/medium.jpg",
            largeImageUrl="https://example.com/large.jpg",
            sampleVoiceUrl="https://example.com/sample.mp3",
            sampleScript="こんにちは",
            recommendedVoiceSpeed=1.2,
            recommendedEmotionalLevel=0.8,
            recommendedSoundDuration=1.0,
            recommendedParameters={
                "emotionalLevel": 0.8,
                "soundDuration": 1.0
            },
            voiceStyles=[
                {"id": 1, "style": "normal"},
                {"id": 2, "style": "happy"}
            ]
        )
        
        assert actor.name_reading == "テストアクター"
        assert actor.birth_month == 7
        assert actor.birth_day == 15
        assert actor.small_image_url == "https://example.com/small.jpg"
        assert isinstance(actor.recommended_parameters, RecommendedParameters)
        assert len(actor.voice_styles) == 2


class TestVoiceGenerationRequest:
    """Tests for VoiceGenerationRequest model."""

    def test_create_minimal_request(self):
        """Test creating VoiceGenerationRequest with minimal fields."""
        request = VoiceGenerationRequest(
            id="actor-1",
            script="こんにちは"
        )
        
        assert request.id == "actor-1"
        assert request.script == "こんにちは"
        assert request.speed == 1.0  # Default value
        assert request.emotional_level is None
        assert request.sound_duration is None
        assert request.format == "mp3"  # Default value

    def test_create_full_request(self):
        """Test creating VoiceGenerationRequest with all fields."""
        request = VoiceGenerationRequest(
            id="actor-1",
            script="こんにちは",
            speed=1.5,
            emotional_level=0.8,
            sound_duration=1.2,
            format="wav"
        )
        
        assert request.id == "actor-1"
        assert request.script == "こんにちは"
        assert request.speed == 1.5
        assert request.emotional_level == 0.8
        assert request.sound_duration == 1.2
        assert request.format == "wav"

    def test_create_request_with_aliases(self):
        """Test creating VoiceGenerationRequest with aliases."""
        request = VoiceGenerationRequest(
            id="actor-1",
            script="こんにちは",
            speed=1.5,
            emotionalLevel=0.8,
            soundDuration=1.2
        )
        
        assert request.emotional_level == 0.8
        assert request.sound_duration == 1.2

    def test_speed_validation(self):
        """Test speed validation."""
        # Valid values
        request = VoiceGenerationRequest(id="actor-1", script="こんにちは", speed=0.4)
        assert request.speed == 0.4
        
        request = VoiceGenerationRequest(id="actor-1", script="こんにちは", speed=3.0)
        assert request.speed == 3.0
        
        # Invalid values
        with pytest.raises(ValidationError):
            VoiceGenerationRequest(id="actor-1", script="こんにちは", speed=0.3)  # Too low
        
        with pytest.raises(ValidationError):
            VoiceGenerationRequest(id="actor-1", script="こんにちは", speed=3.1)  # Too high

    def test_emotional_level_validation(self):
        """Test emotional_level validation."""
        # Valid values
        request = VoiceGenerationRequest(id="actor-1", script="こんにちは", emotional_level=0.0)
        assert request.emotional_level == 0.0
        
        request = VoiceGenerationRequest(id="actor-1", script="こんにちは", emotional_level=1.5)
        assert request.emotional_level == 1.5
        
        # Invalid values
        with pytest.raises(ValidationError):
            VoiceGenerationRequest(id="actor-1", script="こんにちは", emotional_level=-0.1)  # Too low
        
        with pytest.raises(ValidationError):
            VoiceGenerationRequest(id="actor-1", script="こんにちは", emotional_level=1.6)  # Too high

    def test_format_validation(self):
        """Test format validation."""
        # Valid values
        request = VoiceGenerationRequest(id="actor-1", script="こんにちは", format="mp3")
        assert request.format == "mp3"
        
        request = VoiceGenerationRequest(id="actor-1", script="こんにちは", format="wav")
        assert request.format == "wav"
        
        # Invalid values
        with pytest.raises(ValidationError):
            VoiceGenerationRequest(id="actor-1", script="こんにちは", format="flac")

    def test_serializers(self):
        """Test field serializers."""
        request = VoiceGenerationRequest(
            id="actor-1",
            script="こんにちは",
            speed=1.5,
            emotional_level=0.8,
            sound_duration=1.2,
            format="wav"  # Already lowercase since validation happens before serialization
        )
        
        data = request.model_dump(by_alias=True)
        
        # Check serialized values
        assert data["speed"] == "1.5"  # Serialized as string
        assert data["emotionalLevel"] == "0.8"  # Serialized as string
        assert data["soundDuration"] == "1.2"  # Serialized as string
        assert data["format"] == "wav"  # Lowercase conversion


class TestBalance:
    """Tests for Balance model."""

    def test_create_simple_balance(self):
        """Test creating Balance with simple structure."""
        balance = Balance(balance=500)
        assert balance.balance == 500
        assert balance.balances is None
        assert balance.get_credit() == 500

    def test_create_complex_balance(self):
        """Test creating Balance with complex structure."""
        balance = Balance(balances={
            "remainingBalance": 800,
            "credits": [
                {"balance": 500, "type": "regular"},
                {"balance": 300, "type": "bonus"}
            ]
        })
        
        assert balance.balance is None
        assert isinstance(balance.balances, dict)
        assert balance.get_credit() == 800  # Should get remainingBalance

    def test_get_credit_with_balance_field(self):
        """Test get_credit with balance field."""
        balance = Balance(balance=500)
        assert balance.get_credit() == 500

    def test_get_credit_with_remaining_balance(self):
        """Test get_credit with remainingBalance in balances."""
        balance = Balance(balances={"remainingBalance": 800})
        assert balance.get_credit() == 800

    def test_get_credit_with_balance_in_balances(self):
        """Test get_credit with balance in balances."""
        balance = Balance(balances={"balance": 700})
        assert balance.get_credit() == 700

    def test_get_credit_with_credits_list(self):
        """Test get_credit with credits list in balances."""
        balance = Balance(balances={
            "credits": [
                {"balance": 500, "type": "regular"},
                {"balance": 300, "type": "bonus"}
            ]
        })
        assert balance.get_credit() == 500  # Should get first credit balance

    def test_get_credit_with_no_balance_info(self):
        """Test get_credit with no balance information."""
        balance = Balance(balances={"other": "value"})
        assert balance.get_credit() == 0  # Should return 0 if no balance info

    def test_get_credit_with_empty_balance(self):
        """Test get_credit with empty Balance."""
        balance = Balance()
        assert balance.get_credit() == 0