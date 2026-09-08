// Copyright Epic Games, Inc. All Rights Reserved.


#include "Variant_Horror/HorrorPlayerController.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "InputMappingContext.h"
#include "gameCameraManager.h"
#include "HorrorCharacter.h"
#include "HorrorUI.h"
#include "StationDoor.h"
#include "StationOpeningComponent.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "game.h"
#include "Widgets/Input/SVirtualJoystick.h"

AHorrorPlayerController::AHorrorPlayerController()
{
	// set the player camera manager class
	PlayerCameraManagerClass = AgameCameraManager::StaticClass();
}

void AHorrorPlayerController::BeginPlay()
{
	Super::BeginPlay();

	// only spawn touch controls on local player controllers
	if (ShouldUseTouchControls() && IsLocalPlayerController())
	{
		// spawn the mobile controls widget
		MobileControlsWidget = CreateWidget<UUserWidget>(this, MobileControlsWidgetClass);

		if (MobileControlsWidget)
		{
			// add the controls to the player screen
			MobileControlsWidget->AddToPlayerScreen(0);

		} else {

			UE_LOG(Loggame, Error, TEXT("Could not spawn mobile controls widget."));

		}

	}
}

void AHorrorPlayerController::OnPossess(APawn* aPawn)
{
	Super::OnPossess(aPawn);

	// only spawn UI on local player controllers
	if (IsLocalPlayerController())
	{
		// set up the UI for the character
		if (AHorrorCharacter* HorrorCharacter = Cast<AHorrorCharacter>(aPawn))
		{
			// create the UI
			if (!HorrorUI)
			{
				HorrorUI = CreateWidget<UHorrorUI>(this, HorrorUIClass);
				HorrorUI->AddToViewport(0);
			}

			HorrorUI->SetupCharacter(HorrorCharacter);
		}
	}
	
}

void AHorrorPlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();
#if !UE_BUILD_SHIPPING
	InputComponent->BindKey(EKeys::F6, IE_Pressed, this, &AHorrorPlayerController::StationDoorCheckpoint);
#endif
	
	// only add IMCs for local player controllers
	if (IsLocalPlayerController())
	{
		// Add Input Mapping Contexts
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
		{
			for (UInputMappingContext* CurrentContext : DefaultMappingContexts)
			{
				Subsystem->AddMappingContext(CurrentContext, 0);
			}

			// only add these IMCs if we're not using mobile touch input
			if (!ShouldUseTouchControls())
			{
				for (UInputMappingContext* CurrentContext : MobileExcludedMappingContexts)
				{
					Subsystem->AddMappingContext(CurrentContext, 0);
				}
			}
		}
	}	
}

bool AHorrorPlayerController::ShouldUseTouchControls() const
{
	// are we on a mobile platform? Should we force touch?
	return SVirtualJoystick::ShouldDisplayTouchInterface() || bForceTouchControls;
}

void AHorrorPlayerController::StationDoorCheckpoint()
{
#if !UE_BUILD_SHIPPING
	APawn* TestPawn=GetPawn();
	if(!TestPawn || !IsLocalController())return;
	for(TActorIterator<AActor> It(GetWorld());It;++It)
	{
		if(!It->ActorHasTag(TEXT("DoorTestCheckpoint")))continue;
		if(!TestPawn->TeleportTo(It->GetActorLocation(),It->GetActorRotation()))return;
		for(TActorIterator<AStationDoor> Door(GetWorld());Door;++Door)Door->CancelKeypadInteraction();
		if(auto* Opening=TestPawn->FindComponentByClass<UStationOpeningComponent>())Opening->SkipForTesting();
		if(auto* TestCharacter=Cast<ACharacter>(TestPawn)){TestCharacter->GetCharacterMovement()->StopMovementImmediately();TestCharacter->GetCharacterMovement()->SetMovementMode(MOVE_Walking);}
		SetViewTarget(TestPawn);SetControlRotation(It->GetActorRotation());
		ClientMessage(TEXT("Door checkpoint — F6 returns here."));
		return;
	}
#endif
}
