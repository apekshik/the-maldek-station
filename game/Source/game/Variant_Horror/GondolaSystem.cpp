#include "Variant_Horror/GondolaSystem.h"
#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "game.h"
#include "Components/WidgetComponent.h"
#include "InputCoreTypes.h"
#include "StationInteractionStyle.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/SBoxPanel.h"

AGondolaSystem::AGondolaSystem()
{
 PrimaryActorTick.bCanEverTick = true;
 PrimaryActorTick.TickGroup = TG_PrePhysics;
 CablePath = CreateDefaultSubobject<USplineComponent>(TEXT("CablePath"));
 RootComponent = CablePath;
 GondolaMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GondolaMesh"));
 GondolaMesh->SetupAttachment(RootComponent);
 GondolaMesh->SetMobility(EComponentMobility::Movable);
 GondolaMesh->SetCollisionProfileName(FName("BlockAll"));
 DeparturePrompt = CreateDefaultSubobject<UWidgetComponent>(TEXT("DeparturePrompt"));
 DeparturePrompt->SetupAttachment(GondolaMesh);
 DeparturePrompt->SetWidgetSpace(EWidgetSpace::World);
 DeparturePrompt->SetDrawSize(FVector2D(420,90));
 DeparturePrompt->SetTwoSided(true);
 DeparturePrompt->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 DeparturePrompt->SetGenerateOverlapEvents(false);
 DeparturePrompt->SetCastShadow(false);
 DeparturePrompt->SetVisibility(false);
 CreateDoorComponents();
}
void AGondolaSystem::BeginPlay()
{
 Super::BeginPlay();
 using namespace StationInteractionStyle;
 DeparturePrompt->SetSlateWidget(SNew(SBorder).BorderImage(&OuterRule).Padding(2)
  [SNew(SBorder).BorderImage(&Panel).Padding(12)
   [SNew(SVerticalBox)
    +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Text_Lambda([this] { return FText::FromString(bWaitingAtMaldek ? TEXT("E   Return to Millford") : TEXT("E   Depart for Maldek")); }).Font(FCoreStyle::GetDefaultFontStyle("Bold",20)).ColorAndOpacity(StationInteractionStyle::Action)]
    +SVerticalBox::Slot().AutoHeight()[SNew(STextBlock).Text(FText::FromString(TEXT("CROSSING APPROX. 8 MINUTES"))).Font(FCoreStyle::GetDefaultFontStyle("Regular",12)).ColorAndOpacity(StationInteractionStyle::Detail)]]]);
 DeparturePrompt->SetRelativeLocation(FVector(0,210,145));
 DeparturePrompt->SetRelativeRotation(FRotator(0,-90,0));
 DeparturePrompt->SetRelativeScale3D(FVector(.16f));
 DockRouteYaw = CablePath->GetDirectionAtDistanceAlongSpline(0, ESplineCoordinateSpace::World).Rotation().Yaw;
 RouteDistance = 0;
 UpdateGondolaPosition();
 if (IsValid(FarBoardingBridge))
 {
  FarBoardingBridge->GetRootComponent()->SetMobility(EComponentMobility::Movable);
  for (AActor* Part : FarBridgeParts) if (IsValid(Part))
  {
   Part->GetRootComponent()->SetMobility(EComponentMobility::Movable);
   Part->AttachToActor(FarBoardingBridge, FAttachmentTransformRules::KeepWorldTransform);
  }
  FarBoardingBridge->SetActorLocation(FarBridgeParked);
 }
 for (AActor* Part : CabinParts)
 {
  if (!IsValid(Part) || Part == this || !Part->GetRootComponent()) continue;
  Part->GetRootComponent()->SetMobility(EComponentMobility::Movable);
  Part->AttachToComponent(GondolaMesh, FAttachmentTransformRules::KeepWorldTransform);
 }
 if (bStageFirstArrival)
 {
  bArrivalPending = true; bDocked = false;
  RouteDistance = FMath::Clamp(FirstArrivalDistance, 0.f, CablePath->GetSplineLength());
  SetCabinHidden(false);
  UpdateGondolaPosition();
 }
 ApplyDoorPose();
 if (!bStageFirstArrival && HasSlidingDoors()) DoorPhase = EGondolaDoorPhase::Settling;
}
void AGondolaSystem::SetCabinHidden(bool bHideCabin)
{
 GondolaMesh->SetVisibility(!bHideCabin, true);
 for (AActor* Part : CabinParts) if (IsValid(Part)) Part->SetActorHiddenInGame(bHideCabin);
}
void AGondolaSystem::BeginArrival()
{
 if (!bArrivalPending) return;
 bArrivalPending = false; SetCabinHidden(false);
 Direction = -1; CurrentSpeed = ApproachSpeed; bMoving = true;
}
void AGondolaSystem::Tick(float DeltaTime)
{
 Super::Tick(DeltaTime);
 UpdateBoardingBridge(DeltaTime);
 UpdateDoors(DeltaTime);
 const APawn* BoardingPlayer = UGameplayStatics::GetPlayerPawn(this, 0);
 APlayerController* BoardingController = UGameplayStatics::GetPlayerController(this, 0);
 const FVector CabinLocal = BoardingPlayer ? GondolaMesh->GetComponentTransform().InverseTransformPosition(BoardingPlayer->GetActorLocation()) : FVector(0,0,-1000);
 const bool bCanDepart = (bDocked || bWaitingAtMaldek) && !bMoving && !bDepartureRequested && (!HasSlidingDoors() || DoorPhase == EGondolaDoorPhase::Open) && !CabinParts.IsEmpty() && FMath::Abs(CabinLocal.X)<120 && FMath::Abs(CabinLocal.Y)<240 && CabinLocal.Z>30 && CabinLocal.Z<230;
 DeparturePrompt->SetVisibility(bCanDepart);
 if (bCanDepart && BoardingController && BoardingController->WasInputKeyJustPressed(EKeys::E)) { if (bWaitingAtMaldek) ReturnGondola(); else SendGondola(); }
 if (bArrivalPending)
 {
  const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
  const APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
  if (Player && PC && FVector::DistSquared(Player->GetActorLocation(), ArrivalTriggerLocation) <= FMath::Square(ArrivalTriggerRadius))
  {
   FVector Eye; FRotator View; PC->GetPlayerViewPoint(Eye, View);
   const FVector Target = GondolaMesh->GetComponentLocation() + FVector(0,0,170);
   if (FVector::DotProduct(View.Vector(), (Target-Eye).GetSafeNormal()) > .35f)
   {
    FCollisionQueryParams Query(SCENE_QUERY_STAT(GondolaReveal), true, Player);
    Query.AddIgnoredActor(this);
    for (AActor* Part : CabinParts) if (IsValid(Part)) Query.AddIgnoredActor(Part);
    FHitResult Hit;
    if (!GetWorld()->LineTraceSingleByChannel(Hit, Eye, Target, ECC_Visibility, Query)) BeginArrival();
   }
  }
 }
 if (!bMoving || DeltaTime <= 0) return;
 const float Length = CablePath->GetSplineLength();
 if (Length <= KINDA_SMALL_NUMBER) { bMoving = false; return; }
 // Bounded integration steps make acceleration and docking stable in long frames.
 float RemainingTime = DeltaTime;
 while (RemainingTime > 0 && bMoving)
 {
  const float Dt = FMath::Min(RemainingTime, 1.f / 60.f); RemainingTime -= Dt;
  const float Remaining = Direction > 0 ? Length - RouteDistance : RouteDistance;
  const float EndDistance = FMath::Min(RouteDistance, Length - RouteDistance);
  const float Cruise = CruiseSpeed > 0 ? CruiseSpeed : Length / FMath::Max(TravelTime, 1.f);
  const float Blend = FMath::Clamp((EndDistance - SlowZoneDistance) / 2000.f, 0.f, 1.f);
  float TargetSpeed = FMath::Lerp(FMath::Min(ApproachSpeed, Cruise), Cruise, Blend * Blend * (3.f - 2.f * Blend));
  TargetSpeed = FMath::Min(TargetSpeed, FMath::Sqrt(2.f * 16.f * Remaining));
  const float OldSpeed = CurrentSpeed;
  CurrentSpeed = FMath::FInterpConstantTo(CurrentSpeed, TargetSpeed, Dt, FMath::Max(Acceleration, 1.f));
  const float Step = FMath::Min(Remaining, (OldSpeed + CurrentSpeed) * .5f * Dt);
  RouteDistance = FMath::Clamp(RouteDistance + Direction * Step, 0.f, Length);
  if (Remaining - Step <= .5f)
  {
   RouteDistance = Direction > 0 ? Length : 0; CurrentSpeed = 0; bMoving = false;
   CurrentAlpha = RouteDistance / Length; UpdateGondolaPosition(); OnReachedDestination();
  }
 }
 UpdateGondolaPosition();
}
void AGondolaSystem::SendGondola()
{
 if (bMoving || !bDocked || bArrivalPending) return;
 if (HasSlidingDoors()) { RequestDeparture(1.f); return; }
 GetWorld()->GetTimerManager().ClearTimer(MaldekWaitTimer);
 bDocked = false; bMoving = true; Direction = 1; CurrentSpeed = 0;
 OnGondolaDeparted.Broadcast();
 UE_LOG(Loggame, Log, TEXT("Gondola departing for Maldek"));
}
void AGondolaSystem::ReturnGondola()
{
 if (bMoving || bDocked || bArrivalPending) return;
 if (HasSlidingDoors()) { RequestDeparture(-1.f); return; }
 GetWorld()->GetTimerManager().ClearTimer(MaldekWaitTimer);
 if (IsValid(FarBoardingBridge) && !FarBoardingBridge->GetActorLocation().Equals(FarBridgeParked, 1.f))
 { bReturnRequested = true; return; }
 bReturnRequested = false;
 bMoving = true; Direction = -1; CurrentSpeed = 0; bWaitingAtMaldek = false;
 UE_LOG(Loggame, Log, TEXT("Gondola departing Maldek, returning to Millford"));
}
void AGondolaSystem::UpdateBoardingBridge(float DeltaTime)
{
 if (!IsValid(FarBoardingBridge)) return;
 const bool bDoorsHoldBridge = HasSlidingDoors() && DoorPhase != EGondolaDoorPhase::Closed;
 const bool bDeploy = bWaitingAtMaldek && (!bReturnRequested || bDoorsHoldBridge) && !bMoving;
 const FVector Target = bDeploy ? FarBridgeDeployed : FarBridgeParked;
 // Hold the gangway while someone occupies its deck. Never retract it under a rider.
 if (BridgeOccupied()) return;
 const FVector Next = FMath::VInterpConstantTo(FarBoardingBridge->GetActorLocation(), Target, DeltaTime, 120.f);
 FarBoardingBridge->SetActorLocation(Next, false, nullptr, ETeleportType::None);
 if (!HasSlidingDoors() && bReturnRequested && Next.Equals(FarBridgeParked, 1.f)) ReturnGondola();
}
void AGondolaSystem::UpdateGondolaPosition()
{
 if (!CablePath || !GondolaMesh) return;
 const float Length = CablePath->GetSplineLength();
 CurrentAlpha = Length > KINDA_SMALL_NUMBER ? RouteDistance / Length : 0;
 const FVector Location = CablePath->GetLocationAtDistanceAlongSpline(RouteDistance, ESplineCoordinateSpace::World);
 const float Yaw = CablePath->GetDirectionAtDistanceAlongSpline(RouteDistance, ESplineCoordinateSpace::World).Rotation().Yaw;
 // The suspended body stays upright. Reversing travel does not turn the cabin around.
 const FRotator Rotation(0, CabinDockRotation.Yaw + FMath::FindDeltaAngleDegrees(DockRouteYaw, Yaw), 0);
 GondolaMesh->SetWorldLocationAndRotation(Location, Rotation, false, nullptr, ETeleportType::None);
}
void AGondolaSystem::OnReachedDestination()
{
 if (HasSlidingDoors()) { DoorPhase = EGondolaDoorPhase::Settling; DoorPhaseTime = 0.f; }
 if (CurrentAlpha >= 1.f)
 {
  bWaitingAtMaldek = true;
  UE_LOG(Loggame, Log, TEXT("Gondola arrived at Maldek"));
  if (HasSlidingDoors()) return; // Boarding dwell starts after the doors finish opening.
  if (WaitTimeAtMaldek > 0)
   GetWorld()->GetTimerManager().SetTimer(MaldekWaitTimer, this, &AGondolaSystem::ReturnGondola, WaitTimeAtMaldek, false);
  else ReturnGondola();
 }
 else
 {
  bDocked = true; OnGondolaDocked.Broadcast();
  UE_LOG(Loggame, Log, TEXT("Gondola docked at Millford"));
 }
}
