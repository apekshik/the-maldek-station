// Copyright Epic Games, Inc. All Rights Reserved.


#include "Variant_Horror/HorrorPlayerController.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "InputMappingContext.h"
#include "gameCameraManager.h"
#include "HorrorCharacter.h"
#include "HorrorUI.h"
#include "StationDoor.h"
#include "StationInspectionComponent.h"
#include "StationInspectable.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "InputKeyEventArgs.h"
#include "StationOpeningComponent.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "game.h"
#include "Widgets/Input/SVirtualJoystick.h"

AHorrorPlayerController::AHorrorPlayerController()
{
	// set the player camera manager class
	PlayerCameraManagerClass = AgameCameraManager::StaticClass();
	ObjectInspection=CreateDefaultSubobject<UStationInspectionComponent>(TEXT("ObjectInspection"));
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
	ObjectInspection->CancelInspection();
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
	InputComponent->BindKey(EKeys::F7, IE_Pressed, this, &AHorrorPlayerController::StationInspectionDemo);
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
	ObjectInspection->CancelInspection();
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

void AHorrorPlayerController::OnUnPossess()
{
	ObjectInspection->CancelInspection();
	Super::OnUnPossess();
}

bool AHorrorPlayerController::InputKey(const FInputKeyEventArgs& Params)
{
	if(ObjectInspection && Params.Key==EKeys::LeftMouseButton)
	{
		if(Params.Event==IE_Pressed)ObjectInspection->HandlePointerButton(true);
		else if(Params.Event==IE_Released)ObjectInspection->HandlePointerButton(false);
	}
	return Super::InputKey(Params);
}

void AHorrorPlayerController::StationInspectionDemo()
{
#if !UE_BUILD_SHIPPING
	if(!GetPawn() || !IsLocalController())return;
	ObjectInspection->CancelInspection();
	if(auto* Opening=GetPawn()->FindComponentByClass<UStationOpeningComponent>())Opening->SkipForTesting();
	for(TActorIterator<AStationDoor> Door(GetWorld());Door;++Door)Door->CancelKeypadInteraction();
	if(IsMoveInputIgnored() || IsLookInputIgnored())return;
	for(TActorIterator<AStationInspectable> It(GetWorld());It;++It)if(It->ActorHasTag(TEXT("InspectionDemo")))It->Destroy();
	FVector Eye;FRotator View;GetPlayerViewPoint(Eye,View);
	const FVector Forward=FRotator(0,View.Yaw,0).Vector();
	const FVector Candidate=Eye+Forward*110;
	FCollisionQueryParams Query(SCENE_QUERY_STAT(InspectionDemoFloor),false,GetPawn());
	FHitResult Floor;
	if(!GetWorld()->LineTraceSingleByChannel(Floor,Candidate,Candidate-FVector(0,0,300),ECC_Visibility,Query))
	{ClientMessage(TEXT("Inspection demo needs a floor in front of you."));return;}
	UStaticMesh* Asset=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Inspection/SM_InspectionMeter.SM_InspectionMeter"));
	if(!Asset){ClientMessage(TEXT("Import the inspection sample assets first; see game/Inspection.md."));return;}
	FActorSpawnParameters Spawn;Spawn.ObjectFlags|=RF_Transient;
	auto* Object=GetWorld()->SpawnActor<AStationInspectable>(Floor.ImpactPoint+FVector(0,0,1),FRotator(0,View.Yaw+180,0),Spawn);
	if(!Object)return;
	Object->Mesh->SetStaticMesh(Asset);Object->Tags.Add(TEXT("InspectionDemo"));
	Object->DisplayName=FText::FromString(TEXT("Millford service meter"));
	Object->InspectionRotation=FRotator(0,90,0);
	Object->Description=FText::FromString(TEXT("Cable tension diagnostic unit. The reverse carries its service marking."));
	SetControlRotation((Object->GetActorLocation()+FVector(0,0,12)-Eye).Rotation());
	ClientMessage(TEXT("Look at the service meter and press E. F7 places a fresh sample."));
#endif
}
