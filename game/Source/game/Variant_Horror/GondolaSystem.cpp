#include "Variant_Horror/GondolaSystem.h"
#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "game.h"

AGondolaSystem::AGondolaSystem()
{
	PrimaryActorTick.bCanEverTick = true;

	// Create the spline for the cable path
	CablePath = CreateDefaultSubobject<USplineComponent>(TEXT("CablePath"));
	RootComponent = CablePath;

	// Create the gondola mesh
	GondolaMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GondolaMesh"));
	GondolaMesh->SetupAttachment(RootComponent);
	GondolaMesh->SetCollisionProfileName(FName("BlockAll"));
}

void AGondolaSystem::BeginPlay()
{
	Super::BeginPlay();

	// Start docked at Millford (alpha = 0)
	CurrentAlpha = 0.0f;
	UpdateGondolaPosition();
}

void AGondolaSystem::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (!bMoving)
	{
		return;
	}

	// Advance alpha based on travel time and direction
	float DeltaAlpha = (DeltaTime / TravelTime) * Direction;
	CurrentAlpha = FMath::Clamp(CurrentAlpha + DeltaAlpha, 0.0f, 1.0f);

	UpdateGondolaPosition();

	// Check if we've reached either end
	if ((Direction > 0.0f && CurrentAlpha >= 1.0f) || (Direction < 0.0f && CurrentAlpha <= 0.0f))
	{
		bMoving = false;
		OnReachedDestination();
	}
}

void AGondolaSystem::SendGondola()
{
	if (bMoving || !bDocked)
	{
		return;
	}

	bDocked = false;
	bMoving = true;
	Direction = 1.0f;

	OnGondolaDeparted.Broadcast();
	UE_LOG(Loggame, Log, TEXT("Gondola departing for Maldek"));
}

void AGondolaSystem::ReturnGondola()
{
	if (bMoving || bDocked)
	{
		return;
	}

	bMoving = true;
	Direction = -1.0f;
	bWaitingAtMaldek = false;

	UE_LOG(Loggame, Log, TEXT("Gondola departing Maldek, returning to Millford"));
}

void AGondolaSystem::UpdateGondolaPosition()
{
	if (!CablePath)
	{
		return;
	}

	float SplineLength = CablePath->GetSplineLength();
	float Distance = SplineLength * CurrentAlpha;

	FVector Location = CablePath->GetLocationAtDistanceAlongSpline(Distance, ESplineCoordinateSpace::World);
	FRotator Rotation = CablePath->GetRotationAtDistanceAlongSpline(Distance, ESplineCoordinateSpace::World);

	GondolaMesh->SetWorldLocationAndRotation(Location, Rotation);
}

void AGondolaSystem::OnReachedDestination()
{
	if (CurrentAlpha >= 1.0f)
	{
		// Arrived at Maldek — wait, then return automatically
		bWaitingAtMaldek = true;
		UE_LOG(Loggame, Log, TEXT("Gondola arrived at Maldek, waiting %.0f seconds"), WaitTimeAtMaldek);

		GetWorld()->GetTimerManager().SetTimer(
			MaldekWaitTimer,
			this,
			&AGondolaSystem::ReturnGondola,
			WaitTimeAtMaldek,
			false
		);
	}
	else if (CurrentAlpha <= 0.0f)
	{
		// Arrived back at Millford — docked
		bDocked = true;
		UE_LOG(Loggame, Log, TEXT("Gondola docked at Millford"));

		OnGondolaDocked.Broadcast();
	}
}
