#include "SurfaceFootstepComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "Materials/MaterialInterface.h"
#include "PhysicalMaterials/PhysicalMaterial.h"
#include "PhysicsEngine/BodyInstance.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Engine/World.h"

USurfaceFootstepComponent::USurfaceFootstepComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostPhysics;
}

void USurfaceFootstepComponent::BeginPlay()
{
	Super::BeginPlay();
	Character = Cast<ACharacter>(GetOwner());
	if (!Character) { SetComponentTickEnabled(false); return; }
	PreviousLocation = Character->GetActorLocation();
}

void USurfaceFootstepComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!Character) return;
	const FVector Position = Character->GetActorLocation();
	const float Travel = FVector::Dist2D(Position, PreviousLocation);
	PreviousLocation = Position;
	const float Speed = Character->GetVelocity().Size2D();
	// Actual displacement prevents footsteps against walls. Ground/velocity checks also
	// suppress idle moving-platform drift, falling, and teleporting between test locations.
	if (!Character->IsLocallyControlled() || !Character->GetCharacterMovement()->IsMovingOnGround()
		|| Speed < 10.0f || Travel > FMath::Max(200.0f, Speed * DeltaTime * 3.0f))
	{
		DistanceSinceStep = 0.0f;
		return;
	}
	DistanceSinceStep += Travel;
	const float StepDistance = FMath::Max(50.0f, FMath::Lerp(WalkStepDistance, RunStepDistance,
		FMath::Clamp((Speed - 350.0f) / 250.0f, 0.0f, 1.0f)));
	if (DistanceSinceStep >= StepDistance)
	{
		DistanceSinceStep = FMath::Fmod(DistanceSinceStep, StepDistance);
		PlayStep(Speed);
	}
}

void USurfaceFootstepComponent::PlayStep(float Speed)
{
	const FVector Start = Character->GetActorLocation();
	const FVector End = Start - FVector(0, 0, Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() + 45.0f);
	FCollisionQueryParams Query(SCENE_QUERY_STAT(SurfaceFootstep), true, Character);
	Query.bReturnPhysicalMaterial = true;
	Query.bReturnFaceIndex = true;
	FHitResult Hit;
	if (!GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Query))
	{
		// Simple collision-only walkways may not have triangle geometry.
		Hit = Character->GetCharacterMovement()->CurrentFloor.HitResult;
	}
	if (!Hit.bBlockingHit) return;
	UPhysicalMaterial* Physical = Hit.PhysMaterial.Get();
	LastFloorMaterial.Reset();
	if (UPrimitiveComponent* Floor = Hit.GetComponent())
	{
		if (!Physical || Physical->SurfaceType == SurfaceType_Default)
		{
			if (FBodyInstance* Body = Floor->GetBodyInstance()) Physical = Body->GetSimplePhysicalMaterial();
		}
		int32 Section = INDEX_NONE;
		if (UMaterialInterface* Material = Floor->GetMaterialFromCollisionFaceIndex(Hit.FaceIndex, Section))
		{
			LastFloorMaterial = Material->GetName();
			// Material-per-face selection supports metal grating and concrete in one mesh.
			if (UPhysicalMaterial* FacePhysical = Material->GetPhysicalMaterial())
			{
				if (FacePhysical->SurfaceType != SurfaceType_Default) Physical = FacePhysical;
			}
		}
	}
	LastSurface = static_cast<int32>(UPhysicalMaterial::DetermineSurfaceType(Physical));
	const TArray<TObjectPtr<USoundBase>>* Samples = &SoilSteps;
	switch (LastSurface)
	{
	case 2: Samples = &GravelSteps; break;
	case 3: Samples = &MetalSteps; break;
	case 4: Samples = &ConcreteSteps; break;
	case 5: Samples = &WoodSteps; break;
	case 6: Samples = &TileSteps; break;
	default: break;
	}
	if (Samples->IsEmpty()) Samples = &SoilSteps;
	TArray<int32, TInlineAllocator<8>> Valid;
	for (int32 I = 0; I < Samples->Num(); ++I) if ((*Samples)[I]) Valid.Add(I);
	if (Valid.IsEmpty()) return;
	const int32* Previous = PreviousSamples.Find(LastSurface);
	if (Previous && Valid.Num() > 1) Valid.Remove(*Previous);
	const int32 Index = Valid[FMath::RandRange(0, Valid.Num() - 1)];
	PreviousSamples.Add(LastSurface, Index);
	const float RunGain = FMath::GetMappedRangeValueClamped(FVector2D(150, 600), FVector2D(0.8f, 1.2f), Speed);
	// Local first-person body sound; no replicated duplicate on remote pawns.
	UGameplayStatics::PlaySound2D(this, (*Samples)[Index], Volume * RunGain * FMath::FRandRange(0.93f, 1.0f), FMath::FRandRange(0.96f, 1.04f));
	++FootstepCount;
}
