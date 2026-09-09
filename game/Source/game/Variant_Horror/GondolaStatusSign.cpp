#include "Variant_Horror/GondolaStatusSign.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SplineComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

EGondolaPlatformStatus AGondolaSystem::GetPlatformStatus(bool bFarTerminal) const
{
 if (bArrivalPending) return EGondolaPlatformStatus::Away;
 const bool AtTerminal=bFarTerminal ? bWaitingAtMaldek : bDocked;
 if (!bMoving && AtTerminal)
 {
  // An obstruction can reopen the doors while departure remains queued.
  if (bDepartureRequested) return EGondolaPlatformStatus::Depart;
  if (LandingReady() && (!HasSlidingDoors() || DoorPhase==EGondolaDoorPhase::Open))
   return EGondolaPlatformStatus::Board;
  return EGondolaPlatformStatus::Arriving;
 }
 if (bMoving && (bFarTerminal ? Direction>0 : Direction<0))
 {
  const float Remaining=bFarTerminal ? CablePath->GetSplineLength()-RouteDistance : RouteDistance;
  if (Remaining<=SlowZoneDistance) return EGondolaPlatformStatus::Arriving;
 }
 return EGondolaPlatformStatus::Away;
}

AGondolaStatusSign::AGondolaStatusSign()
{
 PrimaryActorTick.bCanEverTick=true;
 PrimaryActorTick.TickInterval=.1f;
 Cabinet=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Cabinet"));
 RootComponent=Cabinet;Cabinet->SetMobility(EComponentMobility::Static);
 Cabinet->SetCollisionProfileName(TEXT("BlockAll"));
 const TCHAR* Names[]={TEXT("Board"),TEXT("Arriving"),TEXT("Depart"),TEXT("Away")};
 for (const TCHAR* Name:Names)
 {
  auto* C=CreateDefaultSubobject<UStaticMeshComponent>(Name);C->SetupAttachment(Cabinet);
  C->SetMobility(EComponentMobility::Static);C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  C->SetCastShadow(false);Circuits.Add(C);
 }
}
void AGondolaStatusSign::BeginPlay()
{
 Super::BeginPlay();
 if (IsValid(Gondola)) AddTickPrerequisiteActor(Gondola);
 for (UStaticMeshComponent* C:Circuits) CircuitMaterials.Add(C->CreateDynamicMaterialInstance(0));
 UpdateStatus();
}
void AGondolaStatusSign::Tick(float DeltaSeconds)
{
 Super::Tick(DeltaSeconds);UpdateStatus();
}
void AGondolaStatusSign::UpdateStatus()
{
 CurrentStatus=IsValid(Gondola) ? Gondola->GetPlatformStatus(bFarTerminal) : EGondolaPlatformStatus::Away;
 for (int32 I=0;I<CircuitMaterials.Num();++I)
  if (CircuitMaterials[I]) CircuitMaterials[I]->SetScalarParameterValue(TEXT("GlowStrength"),I==static_cast<int32>(CurrentStatus) ? LitStrength : UnlitStrength);
}
