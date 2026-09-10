#include "Variant_Horror/GondolaSystem.h"
#include "Components/AudioComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Sound/SoundBase.h"
#include "UObject/ConstructorHelpers.h"

void AGondolaSystem::CreateArrivalAudio()
{
 DockWhooshAudio=CreateDefaultSubobject<UAudioComponent>(TEXT("DockWhooshAudio"));
 DockWhooshAudio->SetupAttachment(GondolaMesh);
 DockWhooshAudio->SetRelativeLocation(FVector(0,0,225));
 DockWhooshAudio->bAutoActivate=false;
 DockWhooshAudio->bOverrideAttenuation=true;
 auto& A=DockWhooshAudio->AttenuationOverrides;
 A.bAttenuate=true;A.bSpatialize=true;
 A.DistanceAlgorithm=EAttenuationDistanceModel::Linear;
 A.AttenuationShape=EAttenuationShape::Sphere;
 A.AttenuationShapeExtents=FVector(550.f);
 A.FalloffDistance=3000.f;
 static ConstructorHelpers::FObjectFinder<USoundBase> Cue(TEXT("/Game/MaldekRefinement/R12/GondolaArrival/Gondola_Dock_Whoosh"));
 DockWhooshSound=Cue.Object;
}

void AGondolaSystem::PlayArrivalAudio()
{
 if (!DockWhooshSound || !DockWhooshAudio) return;
 DockWhooshAudio->SetSound(DockWhooshSound);
 DockWhooshAudio->SetVolumeMultiplier(DockWhooshVolume);
 DockWhooshAudio->Play();
}
